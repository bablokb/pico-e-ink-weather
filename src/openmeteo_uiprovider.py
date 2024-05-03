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

from ui_settings import UI_SETTINGS, COLORS, UI_COLOR_MAP, UI_PALETTE
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
    2: ("\uf002","\uf031"),	#partly cloudy
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
    99:("\uf01d","\uf01d"), 	#Thunderstorm with heavy hail

    # aggregated codes
    1002:("\uf002",),
    1003:("\uf00c",),
    1005:("\uf008",),
    1009:("\uf00a",),
    1017:("\uf0c4",),
    1033:("\uf005",),
    1006:("\uf019",),
    1010:("\uf01b",),
    1018:("\uf014",),
    1034:("\uf005",),
    1012:("\uf0b5",),
    1020:("\uf019",),
    1036:("\uf01e",),
    1024:("\uf01b",),
    1040:("\uf06b",),
    1048:("\uf005",),
    1007:("\uf008",),
    1011:("\uf00a",),
    1019:("\uf003",),
    1035:("\uf005",),
    1013:("\uf006",),
    1021:("\uf008",),
    1037:("\uf010",),
    1025:("\uf00a",),
    1041:("\uf06b",),
    1049:("\uf005",),
    1014:("\uf017",),
    1022:("\uf019",),
    1038:("\uf01e",),
    1026:("\uf01b",),
    1042:("\uf06b",),
    1050:("\uf005",),
    1028:("\uf017",),
    1044:("\uf01d",),
    1052:("\uf01e",),
    1056:("\uf01d",),
    1015:("\uf006",),
    1023:("\uf008",),
    1039:("\uf010",),
    1027:("\uf00a",),
    1043:("\uf06b",),
    1051:("\uf005",),
    1029:("\uf006",),
    1045:("\uf068",),
    1053:("\uf010",),
    1057:("\uf06b",),
    1030:("\uf017",),
    1046:("\uf068",),
    1054:("\uf01e",),
    1058:("\uf01d",),
    1060:("\uf01d",),
    1031:("\uf0b2",),
    1047:("\uf068",),
    1055:("\uf010",),
    1059:("\uf06b",),
    1061:("\uf0b2",),
    1062:("\uf01d",),
    1063:("\uf068",)
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

  def __init__(self,debug=False):
    """ constructor: create ressources """

    self._debug       = debug
    self._large_font  = bitmap_font.load_font(UI_SETTINGS.LARGE_FONT)
    self._small_font  = bitmap_font.load_font(UI_SETTINGS.SMALL_FONT)
    self._wdir_font   = bitmap_font.load_font(UI_SETTINGS.WDIR_FONT)
    self._wicon_font  = bitmap_font.load_font(UI_SETTINGS.WICON_FONT)
    self._margin      = UI_SETTINGS.MARGIN
    self._padding     = UI_SETTINGS.PADDING
    self._model       = {}
    self._frame       = None

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
    # note: current-temp is slightly moved to the right using a fixed
    #       offset. The dynamic solution would be to measure the size of "°"
    g.append(
      label.Label(self._large_font,
                  text=f"{self._model['current'].temp}°",
                  color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                  anchor_point=(0.5,0),
                  anchored_position=(b_width2+3*self._margin,
                                     2*self._margin)))

    wdir_char = OpenMeteoUIProvider.DIR_MAP[
      self._model["current"].wind_dir]
    g.append(label.Label(self._wdir_font,text=wdir_char,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       anchor_point=(0.5,0.5),
                       anchored_position=(b_width2,b_height2
                                          )))

    speed_txt = f"{self._model['current'].wind_speed} {self._model['units']['wind_speed']}"
    g.append(label.Label(self._small_font,text=speed_txt,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       anchor_point=(0.5,1),
                       anchored_position=(b_width2,
                                          b_height-self._margin)))

    # hours
    for i in range(3):
      h_data = self._model["hours"][i]
      h_txt1  = f"{h_data.hour}:00"
      h_txt2  = f"{h_data.temp}°"
      h_txt1_label = label.Label(self._small_font,text=h_txt1,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       anchor_point=(0.5,0),
                       anchored_position=(
                             self._margin+(i+1)*(b_width+1)+b_width2,
                             2*self._margin))
      g.append(h_txt1_label)
      g.append(label.Label(self._small_font,text=h_txt2,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       anchor_point=(0.5,0),
                       anchored_position=(
                             self._margin+(i+1)*(b_width+1)+b_width2,
                             2*self._margin+h_txt1_label.bounding_box[3]+6)))

      icon = self._map_wmo(h_data.wmo,h_data.is_day)
      g.append(label.Label(self._wicon_font,text=icon,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       background_tight=True,
                       anchor_point=(0.5,0.15),
                       anchored_position=(self._margin+(i+1)*b_width+b_width2,
                                          b_height2)))

    # days
    for i in range(4):
      d_data = self._model["days"][i]
      d_txt1 = f"{UI_SETTINGS.UI_DAYS[d_data.wday]} {d_data.day}.{d_data.month}."
      d_txt2 = f"{d_data.tmin}°/{d_data.tmax}°"
      d_txt1_label = label.Label(self._small_font,text=d_txt1,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       anchor_point=(0.5,0.00),
                       anchored_position=(
                             i*(b_width+1)+b_width2,
                             b_height+1+self._margin))
      g.append(d_txt1_label)
      g.append(label.Label(self._small_font,text=d_txt2,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       anchor_point=(0.5,0.00),
                       anchored_position=(
                             i*(b_width+1)+b_width2,
                             b_height+1+self._margin+
                             d_txt1_label.bounding_box[3]+6)))

      icon = self._map_wmo(d_data.wmo)
      g.append(label.Label(self._wicon_font,text=icon,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       background_tight=True,
                       anchor_point=(0.5,0.3),
                       anchored_position=(self._margin+i*(b_width+1)+b_width2,
                                          b_height+1+b_height2)))

      sun_hours = f"{d_data.sun_hours}h"
      g.append(label.Label(self._small_font,text=sun_hours,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       anchor_point=(0.00,1.00),
                       anchored_position=(
                             i*(b_width+1),
                             2*b_height-self._margin-1)))

      prec_hours = f"{d_data.prec_hours}h"
      g.append(label.Label(self._small_font,text=prec_hours,
                       color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                       anchor_point=(1.00,1.00),
                       anchored_position=(
                             (i+1)*(b_width)-self._margin,
                             2*b_height-self._margin-1)))
    return g

  # --- update data   --------------------------------------------------------

  def update_ui(self,new_data):
    """ update data: callback for Application """

    # update model
    self._model.update(new_data)

    # map values for day and month
    self._model["day"]  = self._model["current"].day
    self._model["date"] = UI_SETTINGS.UI_MONTHS[int(self._model["current"].month)-1]
    self._model["now"]  = self._model["current"].update

    # remove old header, footer, grid (keep background)
    if len(self._frame_group) == 4:
      for _ in range(3):
        self._frame_group.pop()
      gc.collect()

    (header,h_header) = self._frame.get_header()
    self._frame_group.append(header)
    (footer,h_footer) = self._frame.get_footer()
    self._frame_group.append(footer)
    gc.collect()

    # create layout for weather
    grid = self._get_grid(self._width,self._height - h_header - h_footer)
    grid.x = self._margin
    grid.y = h_header
    self._frame_group.append(grid)

  # --- create complete content   --------------------------------------------

  def create_ui(self,display):
    """ create content """

    if not self._frame:
      self._width       = display.width
      self._height      = display.height
      self._frame       = Frame(display,self._model)
      self._frame_group = self._frame.create_group()
    return self._frame_group

  # --- handle exception   ---------------------------------------------------

  def handle_exception(self,ex):
    """ handle exception """

    traceback.print_exception(ex)

    # optional:
    #   - save exception here
    #   - create different content in create_content() if exception occured
