# ----------------------------------------------------------------------------
# wifi_helper_builtin.py: Wifi-helper for builtin wifi
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# ----------------------------------------------------------------------------

import board
import time
import socketpool
import adafruit_requests

from settings import secrets

class WifiHelper:
  """ Wifi-Helper for MCU with integrated wifi """

  # --- constructor   --------------------------------------------------------

  def __init__(self,debug=False):
    """ constructor """

    self._debug = debug
    if not hasattr(secrets,'channel'):
      secrets.channel = 0
    if not hasattr(secrets,'timeout'):
      secrets.timeout = None

    self._wifi = None

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- initialze and connect to AP and to remote-port   ---------------------

  def connect(self):
    """ initialize connection """

    import wifi
    self._wifi = wifi
    self.msg("connecting to %s" % secrets.ssid)
    retries = secrets.retry
    while True:
      try:
        wifi.radio.connect(secrets.ssid,
                          secrets.password,
                           channel = secrets.channel,
                           timeout = secrets.timeout
                           )
        break
      except:
        self.msg("could not connect to %s" % secrets.ssid)
        retries -= 1
        if retries == 0:
          raise
        time.sleep(1)
        continue
    self.msg("connected to %s" % secrets.ssid)
    pool = socketpool.SocketPool(wifi.radio)
    self._requests = adafruit_requests.Session(pool)

  # --- return implementing wifi   -----------------------------------------

  @property
  def wifi(self):
    """ return wifi """
    return self._wifi

  # --- execute get-request   -----------------------------------------------

  def get_json(self,url):
    """ process get-request """

    return self._requests.get(url).json()
