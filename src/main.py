# -------------------------------------------------------------------------
# Display weather-data (current and forecast) on an e-paper display.
#
# This program needs an additional configuration file settings.py
# with wifi-credentials and application settings.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import sys
import time
try:
  import pygame
except:
  # running CircuitPython on a MCU
  pass

from application import Application
from openmeteo_uiprovider   import OpenMeteoUIProvider   as UIProvider
from openmeteo_dataprovider import OpenMeteoDataProvider as DataProvider
from settings import app_config
from ui_settings import UI_SETTINGS

DEBUG = getattr(app_config,'debug',False)

class OpenMeteo(Application):
  """ OpenMeteo main-application class """

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """
    ui_provider   = UIProvider(debug=DEBUG)
    data_provider = DataProvider(debug=DEBUG)
    super().__init__(data_provider,ui_provider,with_rtc=False,debug=DEBUG)
    self.blink(0.1,color=Application.GREEN)

    self.data["last_update"] = "unknown"
    self._last_run = 0
    self._next_update = 0

  # --- calculate interval until next update   -------------------------------

  def _calc_next_update_time(self):
    """ return interval until next update is due """

    if self.data["last_update"] == "unknown":
      # very first update - start with 5 minutes
      self.data["last_update"] = self.data["current"].update
      interval = 300
    elif self.data["last_update"] == self.data["current"].update:
      # no change - keep 5 minutes
      interval = 300
    else:
      # data was updated - use interval of data
      self.data["last_update"] = self.data["current"].update
      interval = self.data["current"].interval

    self.msg(f"calculated interval for next update: {interval}")
    self._next_update = self._last_run + interval

  # --- main code (override base class)   ------------------------------------

  def run(self):
    """ main code """

    if time.monotonic() < self._next_update:
      # nothing to do yet
      return
    else:
      # execute standard code and update timings
      super().run()
      self._last_run = time.monotonic()
      self._calc_next_update_time()

  # --- key-handler for PyGame-Display environment   -------------------------

  def on_event(self,ev):
    """ process key-press """

    if ev.key in [pygame.K_ESCAPE,pygame.K_q]:
      sys.exit(0)

  # --- main loop for PyGame-Display environment   ---------------------------

  def run_pygame(self):
    """ event-loop for PyGame-Display environment """

    self.run()
    self.display.event_loop(
      interval=60,
      on_time=self.run, on_event=self.on_event, events=[pygame.KEYDOWN])

  # --- main loop for normal CircuitPython environment   ---------------------

  def run_cp(self):
    """ main-loop for normal environment """

    while True:
      self.run()
      self.sleep(60)        # check once a minute if an update is necessary

# --- main application code   -------------------------------------------------

app = OpenMeteo()
if app.is_pygame:
  app.run_pygame()
else:
  app.run_cp()
