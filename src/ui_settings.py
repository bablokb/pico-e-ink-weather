# -------------------------------------------------------------------------
# Display weather-data (current and forecast) on an ACEP e-paper display.
#
# This file contains settings related to the UI.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# -------------------------------------------------------------------------

from displayio import Palette

class Settings:
  pass

UI_PALETTE = Palette(7)
UI_PALETTE[0] = 0xFFFFFF
UI_PALETTE[1] = 0x000000
UI_PALETTE[2] = 0x0000FF
UI_PALETTE[3] = 0x00FF00
UI_PALETTE[4] = 0xFF0000
UI_PALETTE[5] = 0xFFFF00
UI_PALETTE[6] = 0xFFA500

COLORS = Settings()
COLORS.WHITE  = 0
COLORS.BLACK  = 1
COLORS.BLUE   = 2
COLORS.GREEN  = 3
COLORS.RED    = 4
COLORS.YELLOW = 5
COLORS.ORANGE = 6

# map color-names to (BG_COLOR,FG_COLOR)
UI_COLOR_MAP = {
  "white":  (COLORS.WHITE,COLORS.BLACK),
  "black":  (COLORS.BLACK,COLORS.WHITE),
  "blue":   (COLORS.BLUE,COLORS.WHITE),
  "green":  (COLORS.GREEN,COLORS.BLACK),
  "red":    (COLORS.RED,COLORS.BLACK),
  "yellow": (COLORS.YELLOW,COLORS.BLACK),
  "orange": (COLORS.ORANGE,COLORS.BLACK)
  }

UI_SETTINGS = Settings()
UI_SETTINGS.LARGE_FONT  = "fonts/DejaVuSerif-32.bdf"
UI_SETTINGS.SMALL_FONT  = "fonts/DejaVuSerif-18.bdf"
UI_SETTINGS.WDIR_FONT   = "fonts/WeatherIcons-Regular-40.bdf"
UI_SETTINGS.WICON_FONT  = "fonts/WeatherIcons-Regular-46.bdf"
UI_SETTINGS.DAY_FONT    =  "fonts/DejaVuSerif-Bold-60.bdf"
UI_SETTINGS.DATE_FONT   = "fonts/DejaVuSans-BoldOblique-35.bdf"
UI_SETTINGS.MARGIN =    3
UI_SETTINGS.PADDING =   3
UI_SETTINGS.FOREGROUND = COLORS.BLACK
UI_SETTINGS.BACKGROUND = COLORS.WHITE
UI_SETTINGS.NO_NETWORK = "images/no-server-connection.bmp"
UI_SETTINGS.NO_EVENTS  = "images/empty-agenda.bmp"

UI_SETTINGS.UI_MONTHS = [
  "January", "February", "March",     "April",   "May",      "June",
  "July",    "August",   "September", "October", "November", "December"
  ]
UI_SETTINGS.UI_DAYS = [
  "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"
  ]
UI_SETTINGS.FOOTER = "Updated"

# overrides from settings

try:
  from settings import ui_config
  for var in dir(ui_config):
    if var[0] != '_':
      setattr(UI_SETTINGS,var,getattr(ui_config,var))
except:
  pass
