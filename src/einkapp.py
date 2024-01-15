# -------------------------------------------------------------------------
# Generic class for e-ink based applications.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import builtins
import time
import board
import traceback

# import board-specific implementations
try:
  config_file = "config."+board.board_id.replace(".","_")
  hw_impl = builtins.__import__(config_file,None,None,["config"],0)
  print("using board-specific implementation")
except Exception as ex:
  print(f"!!! error or no board specific config: {ex}. Trouble ahead !!!")
  config_file = "config.def_config"
  hw_impl = builtins.__import__(config_file,None,None,["config"],0)
  print("using default implementation")

from config.secrets import app_config

# --- application class   ----------------------------------------------------

class EInkApp:

  # --- constructor   --------------------------------------------------------

  def __init__(self,dataprovider,uiprovider,with_rtc=True):
    """ constructor """

    self._setup(with_rtc)  # setup hardware
    if with_rtc and self._rtc_ext:
      self._rtc_ext.update_time(app_config.time_url)
    dataprovider.set_wifi(self.wifi)

    self._dataprovider = dataprovider
    self._uiprovider   = uiprovider

  # --- setup hardware   -----------------------------------------------------

  def _setup(self,with_rtc):
    """ setup hardware """
    
    self.display    = hw_impl.config.get_display()
    self.is_pygame  = hasattr(self.display,"check_quit")
    self.bat_level  = hw_impl.config.bat_level
    self._led       = hw_impl.config.status_led
    self.wifi       = hw_impl.config.wifi()
    self._shutdown  = hw_impl.config.shutdown
    if with_rtc:
      self._rtc_ext = hw_impl.config.get_rtc_ext()
      if self._rtc_ext:
        self._rtc_ext.set_wifi(self.wifi)

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    start = time.monotonic()
    self.data = {}
    self.data["bat_level"] = self.bat_level()
    self._dataprovider.update_data(self.data)
    self._uiprovider.update_data(self.data)

  # --- update display   -----------------------------------------------------

  def update_display(self,content):
    """ update display """

    start = time.monotonic()
    if self.is_pygame:
      self.display.show(content)
    else:
      self.display.root_group = content
    print(f"update_display (show): {time.monotonic()-start:f}s")
    start = time.monotonic()

    if not self.is_pygame and self.display.time_to_refresh > 0.0:
      import alarm
      # ttr will be >0 only if system is on USB-power (running...)
      print(f"time-to-refresh: {self.display.time_to_refresh}")
      time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic()+self.display.time_to_refresh)
      alarm.light_sleep_until_alarms(time_alarm)

    self.display.refresh()
    duration = time.monotonic()-start
    print(f"update_display (refreshed): {duration:f}s")

    if not self.is_pygame:
      update_time = self.display.time_to_refresh - duration
      if update_time > 0.0:
        print(f"update-time: {update_time} (sleeping...)")
        time_alarm = alarm.time.TimeAlarm(
          monotonic_time=time.monotonic()+update_time)
        alarm.light_sleep_until_alarms(time_alarm)
        print("update finished!")

  # --- blink status-led   ---------------------------------------------------

  def blink(self,duration):
    """ blink status-led once for the given duration """
    self._led(1)
    time.sleep(duration)
    self._led(0)

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device """
    self._shutdown()

  # --- main application code   ----------------------------------------------

  def run(self):
    """ main application loop """

    try:
      self.update_data()
    except Exception as ex:
      try:
        self._uiprovider.handle_exception(ex)
      except Exception as ex2:
        # cannot do anything here
        traceback.print_exception(ex2)
    finally:
      content = self._uiprovider.create_content(self.display)
      self.update_display(content)
    self.shutdown()

    # we should not be here ;-)
    time.sleep(60)
