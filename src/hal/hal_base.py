# ----------------------------------------------------------------------------
# HalBase: Hardware-Abstraction-Layer base-class.
#
# This class implements standard methods. If necessary, some of them must be
# overridden by board-specific sub-classes.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
# ----------------------------------------------------------------------------

import board
import time
try:
  import alarm
except:
  pass
from digitalio import DigitalInOut, Direction

class HalBase:
  def __init__(self):
    """ constructor """
    self._display = None

  def _init_led(self):
    """ initialize LED/Neopixel """
    if hasattr(board,'NEOPIXEL'):
      if not hasattr(self,'_pixel'):
        if hasattr(board,'NEOPIXEL_POWER'):
          # need to do this first,
          # https://github.com/adafruit/Adafruit_CircuitPython_MagTag/issues/75
          self._pixel_poweroff = DigitalInOut(board.NEOPIXEL_POWER)
          self._pixel_poweroff.direction = Direction.OUTPUT
        import neopixel
        self._pixel = neopixel.NeoPixel(board.NEOPIXEL,1,
                                        brightness=0.1,auto_write=False)
    elif hasattr(board,'LED'):
      if not hasattr(self,'_led'):
        self._led = DigitalInOut(board.LED)
        self._led.direction = Direction.OUTPUT

    # replace method with noop
    self._init_led = lambda: None

  def led(self,value,color=[255,0,0]):
    """ set status LED/Neopixel """
    self._init_led()
    if hasattr(self,'_led'):
      self._led.value = value
    elif hasattr(self,'_pixel'):
      if hasattr(self,'_pixel_poweroff'):
        self._pixel_poweroff.value = not value
      if value:
        self._pixel.fill(color)
        self._pixel.show()

  def bat_level(self):
    """ return battery level """
    if hasattr(board,"VOLTAGE_MONITOR"):
      from analogio import AnalogIn
      adc = AnalogIn(board.VOLTAGE_MONITOR)
      level = adc.value *  3 * 3.3 / 65535
      adc.deinit()
      return level
    else:
      return 0.0

  def wifi(self,debug=False):
    """ return wifi-interface """
    from wifi_helper_builtin import WifiHelper
    return WifiHelper(debug=debug)

  def get_display(self):
    """ return display """
    if not self._display:
      if hasattr(board,'DISPLAY'):           # try builtin display
        self._display = board.DISPLAY
      else:                                  # try display from settings
        try:
          from settings import hw_config
          self._display = hw_config.get_display()
        except:
          self._display = None
    return self._display

  def show(self,content):
    """ show and refresh the display """

    self._display.root_group = content

    while self._display.time_to_refresh > 0.0:
      # ttr will be >0 only if system is on running on USB-power
      time.sleep(self._display.time_to_refresh)

    start = time.monotonic()
    while True:
      try:
        self._display.refresh()
        break
      except RuntimeError:
        pass
    duration = time.monotonic()-start

    update_time = self._display.time_to_refresh - duration
    if update_time > 0.0:
      # might running on battery-power: save some power using light-sleep
      time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic()+update_time)
      alarm.light_sleep_until_alarms(time_alarm)

  def get_rtc_ext(self):
    """ return external rtc, if available """
    try:
      from settings import hw_config
      return hw_config.get_rtc()
    except:
      return None

  def shutdown(self):
    """ shutdown system """
    pass

  def reset_if_needed(self):
    """ reset device (workaround for MemoryError) """
    pass

  def sleep(self,duration):
    """ sleep for the given duration in seconds """
    time.sleep(duration)

  def get_keys(self):
    """ return list of pin-numbers for up, down, left, right """
    # format is (active-state,[key1,...])
    try:
      from settings import hw_config
      return hw_config.get_keys()
    except:
      return None
