# ----------------------------------------------------------------------------
# settings_template.py: Credentials, Hardware, UI and application settings.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# ----------------------------------------------------------------------------

class Settings:
  pass

# network configuration   ----------------------------------------------------

secrets  = Settings()
secrets.ssid      = 'my_ssid'
secrets.password  = 'my_secret_password'
secrets.retry     = 2
secrets.debugflag = False
#secrets.channel   = 6           # optional
#secrets.timeout   = 10          # optional

# hardware configuration (optional)  -----------------------------------------

hw_config = Settings()
def _get_display(hal):
  from blinka_displayio_pygamedisplay import PyGameDisplay
  return PyGameDisplay(width=400,height=300,
                       native_frames_per_second=1)
def _get_rtc():
  # currently not supported/unused
  return None

hw_config.DISPLAY  = _get_display
hw_config.get_rtc  = _get_rtc

# changes to UI-defaults (see ui_settings.py for a list)   -------------------

ui_config = Settings()
ui_config.UI_MONTHS = [
  "Januar", "Februar", "März",      "April",   "Mai",      "Juni",
  "Juli",   "August",  "September", "Oktober", "November", "Dezember"
  ]
ui_config.UI_DAYS = [
  "Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"
  ]
ui_config.FOOTER = "Aktualisiert"

# app configuration   --------------------------------------------------------

app_config = Settings()
app_config.longitude = 13.4105
app_config.latitude  = 52.5244
app_config.debug = False

# all settings   -------------------------------------------------------------

settings = Settings()
settings.secrets     = secrets
settings.hw_config   = hw_config
settings.app_config  = app_config
settings.ui_config   = ui_config
