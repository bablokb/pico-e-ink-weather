# -------------------------------------------------------------------------
# Display weather-data (current and forecast) on an ACEP e-paper display.
#
# This class implements the actual layout of all items on the display.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# -------------------------------------------------------------------------

import time
import gc
import displayio
import traceback

from vectorio import Rectangle
from adafruit_display_text import label
from adafruit_display_shapes.line import Line
from adafruit_bitmap_font import bitmap_font

from ui_settings import UI_SETTINGS, COLORS, UI_COLOR_MAP, UI_PALETTE, UI_MONTHS, UI_DAYS
from frame import Frame

# --- OpenMeteo Class for layout   -------------------------------------------

class OpenMeteoUIProvider:

  # map wmo to icon: wmo: (day,night). Only a few
  # conditions (cloudy, sunny) map to different night icons, although a
  # complete set of night-icons would be available

  WMO_MAP = {
    # Code 	Description
    0: ("\uf00d","\uf077"), 	#Clear sky
    1: ("\uf00c","\uf083"),	#Mainly clear
    2: ("\uf013","\uf013"),	#partly cloudy
    3: ("\uf041","\uf041"),	#overcast
    45:("\uf021","\uf021"), 	#Fog
    48:("\uf021","\uf021"), 	#depositing rime fog
    51:("\uf01c","\uf01c"), 	#Drizzle: light
    53:("\uf01c","\uf01c"), 	#Drizzle: moderate
    55:("\uf01c","\uf01c"), 	#Drizzle: dense
    56:("\uf0b5","\uf0b5"), 	#Freezing Drizzle: Light
    57:("\uf0b5","\uf0b5"), 	#Freezing Drizzle: dense
    61:("\uf019","\uf019"), 	#Rain: Slight
    63:("\uf019","\uf019"), 	#Rain: moderate
    65:("\uf019","\uf019"), 	#Rain: heavy
    66:("\uf0b5","\uf0b5"), 	#Freezing Rain: Light
    67:("\uf017","\uf017"), 	#Freezing Rain: heavy
    71:("\uf01b","\uf01b"), 	#Snow fall: Slight
    73:("\uf01b","\uf01b"), 	#Snow fall: moderate
    75:("\uf064","\uf064"), 	#Snow fall: heavy
    77:("\uf01b","\uf01b"), 	#Snow grains
    80:("\uf01c","\uf01c"), 	#Rain showers: Slight
    81:("\uf01a","\uf01a"), 	#Rain showers: moderate
    82:("\uf015","\uf015"), 	#Rain showers: violent
    85:("\uf01b","\uf01b"), 	#Snow showers slight
    86:("\uf064","\uf064"), 	#Snow showers heavy
    95:("\uf01e","\uf01e"), 	#Thunderstorm: Slight or moderate
    96:("\uf01d","\uf01d"), 	#Thunderstorm with slight  hail
    99:("\uf01d","\uf01d") 	#Thunderstorm with heavy hail
    }

  # map wind-direction to unicode-char in font
  DIR_MAP = {
    "N":  "\uF060",
    "NE": "\uF05E",
    "E":  "\uF061",
    "SE": "\uF05B",
    "S":  "\uF05C",
    "SW": "\uF05A",
    "W":  "\uF059",
    "NW": "\uF05D"
    }

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor: create ressources """

    self._large_font  = bitmap_font.load_font(UI_SETTINGS.LARGE_FONT)
    self._small_font  = bitmap_font.load_font(UI_SETTINGS.SMALL_FONT)
    self._wdir_font   = bitmap_font.load_font(UI_SETTINGS.WDIR_FONT)
    self._wicon_font  = bitmap_font.load_font(UI_SETTINGS.WICON_FONT)
    self._margin      = UI_SETTINGS.MARGIN
    self._padding     = UI_SETTINGS.PADDING
    self._model       = {}

  # --- map wmo to char of WI-font   -----------------------------------------

  def _map_wmo(self,wmo,is_day=True):
    """ map wmo to char of WI-font """

    if wmo in OpenMeteoUIProvider.WMO_MAP:
      return OpenMeteoUIProvider.WMO_MAP[wmo][not is_day]
    else:
      # otherwise return default ("n/a")
      return "\uf07b"

  # --- helper method for debugging   ----------------------------------------

  def print_size(self,label,obj):
    """ print size of object """
    print(f"{label} w,h: {obj.width},{obj.height}")

  # --- get grid of forecast-boxes   -----------------------------------------

  def _get_grid(self,width,height):
    """ get grid of forecast-boxes """

    b_width   = int(width/4)
    b_width2  = int(width/8)
    b_height  = int(height/2)
    b_height2 = int(height/4)
    g        = displayio.Group()

    # horizontal line
    g.append(Line(0,b_height,width,b_height,
                  color=UI_PALETTE[UI_SETTINGS.FOREGROUND]))
    # vertical lines
    for i in range(1,4):
      g.append(Line(i*b_width,0,i*b_width,height,
                 color=UI_PALETTE[UI_SETTINGS.FOREGROUND]))
    # current day
    g.append(
      label.Label(self._large_font,
                  text=f"{self._model['current'].temp}°",
                  color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                  background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                  anchor_point=(0.5,0),
                  anchored_position=(b_width2,
                                     self._margin)))

    wdir_char = OpenMeteoUIProvider.DIR_MAP[
      self._model["current"].wind_dir]
    g.append(label.Label(self._wdir_font,text=wdir_char,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                       anchor_point=(0.5,0.5),
                       anchored_position=(b_width2,b_height2
                                          )))

    speed_txt = f"{self._model['current'].wind_speed} {self._model['units']['wind_speed']}"
    g.append(label.Label(self._small_font,text=speed_txt,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                       anchor_point=(0.5,1),
                       anchored_position=(b_width2,
                                          b_height-self._margin)))

    # hours
    for i in range(3):
      h_data = self._model["hours"][i]
      h_txt  = f"{h_data.hour}:00\n{h_data.temp}°"
      g.append(label.Label(self._small_font,text=h_txt,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                       line_spacing = 0.8,
                       anchor_point=(0.5,0),
                       anchored_position=(
                             self._margin+(i+1)*(b_width+1)+b_width2,
                             self._margin)))

      icon = self._map_wmo(h_data.wmo,h_data.is_day)
      g.append(label.Label(self._wicon_font,text=icon,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                       background_tight=True,
                       anchor_point=(0.5,0.15),
                       anchored_position=(self._margin+(i+1)*b_width+b_width2,
                                          b_height2)))

    # days
    for i in range(4):
      d_data = self._model["days"][i]
      d_txt  = f"{UI_DAYS[d_data.wday]} {d_data.day}.{d_data.month}.\n"
      d_txt += f"{d_data.tmin}°/{d_data.tmax}°"
      g.append(label.Label(self._small_font,text=d_txt,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                       line_spacing = 0.8,
                       anchor_point=(0.5,0.00),
                       anchored_position=(
                             i*(b_width+1)+b_width2,
                             b_height+1+self._margin)))

      icon = self._map_wmo(d_data.wmo)
      g.append(label.Label(self._wicon_font,text=icon,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                       background_tight=True,
                       anchor_point=(0.5,0.15),
                       anchored_position=(self._margin+i*(b_width+1)+b_width2,
                                          b_height+1+b_height2)))
    return g

  # --- update data   --------------------------------------------------------

  def update_data(self,new_data):
    """ update data: callback for E-Ink-App """

    # update model
    self._model.update(new_data)

    # map values for day and month
    self._model["day"]  = self._model["current"].day
    self._model["date"] = UI_MONTHS[int(self._model["current"].month)-1]
    self._model["now"]  = self._model["current"].update

  # --- create complete content   --------------------------------------------

  def create_content(self,display):
    """ create content """

    frame = Frame(display,self._model)

    g = frame.get_group()
    (header,h_header) = frame.get_header()
    g.append(header)
    (footer,h_footer) = frame.get_footer()
    g.append(footer)
    gc.collect()

    # create layout for weather
    width  = display.width
    height = display.height - h_header - h_footer
    grid = self._get_grid(width,height)
    grid.x = self._margin
    grid.y = h_header
    g.append(grid)

    return g

  # --- handle exception   ---------------------------------------------------

  def handle_exception(self,ex):
    """ handle exception """

    traceback.print_exception(ex)

    # optional:
    #   - save exception here
    #   - create different content in create_content() if exception occured
