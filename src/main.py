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

  # --- key-handler for PyGame-Display environment   -------------------------

  def on_event(self,ev):
    """ process key-press """

    if ev.key in [pygame.K_ESCAPE,pygame.K_q]:
      sys.exit(0)

  # --- event-handler for PyGame-Display environment   -----------------------

  def on_time(self):
    """ process regular action """
    # TODO: only run if OpenMeteo update-interval has expired
    self.run()

  # --- main loop for PyGame-Display environment   ---------------------------

  def run_pygame(self):
    """ event-loop for PyGame-Display environment """

    self.run()
    self.display.event_loop(
      interval=60,
      on_time=self.on_time, on_event=self.on_event, events=[pygame.KEYDOWN])

  # --- main loop for normal CircuitPython environment   ---------------------

  def run_cp(self):
    """ main-loop for normal environment """

    while True:
      start = time.monotonic()
      self.run()
      # TODO: sleep for OpenMeteo update-interval
      self.sleep(60 - (time.monotonic()-start))

# --- main application code   -------------------------------------------------

app = OpenMeteo()
if app.is_pygame:
  app.run_pygame()
else:
  app.run_cp()
