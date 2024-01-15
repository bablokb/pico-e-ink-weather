# ----------------------------------------------------------------------------
# GENERIC_LINUX_PC.py: HW-config for simulation with PygameDisplay
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# ----------------------------------------------------------------------------

import sys
import time
import board
from blinka_displayio_pygamedisplay import PyGameDisplay
from hwconfig import HWConfig
class PygameConfig(HWConfig):
  """ GENERIC_LINUX_PC specific configuration-class """

  def get_display(self):
    """ return display """
    self._display = PyGameDisplay(width=600,height=448,
                                  native_frames_per_second=1)
    return self._display

  def bat_level(self):
    """ return battery level """
    return 3.6

  def status_led(self,value):
    """ set status LED """
    pass

  def wifi(self):
    """ return wifi-interface """
    from wifi_helper_generic import WifiHelper
    return WifiHelper(debug=True)

  def shutdown(self):
    """ leave program (here: wait for quit)"""
    while True:
      if self._display.check_quit():
        sys.exit(0)
      time.sleep(0.25)

config = PygameConfig()
