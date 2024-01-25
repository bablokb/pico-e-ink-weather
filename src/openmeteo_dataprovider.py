# -------------------------------------------------------------------------
# Display weather-data (current and forecast) on an ACEP e-paper display.
#
# Interface to Open-Meteo API.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# -------------------------------------------------------------------------

import json, time

from settings import app_config

# --- helper class (value-holder)   ------------------------------------------

class Values(object):
  def print(self):
    for key,value in vars(self).items():
      print(f"{key} = {value}")

# --- interface to Open-Meteo API (subset)   ---------------------------------

class OpenMeteoDataProvider:

  # wind-direction constants
  DIRECTION = ['N','NE','E','SE','S','SW','W','NW','N']

  # Open-Meteo variables (current/hourly)
  OM_HOURLY = ",".join([
    "is_day",
    "weathercode",
    "temperature_2m",
    "relativehumidity_2m",
    "precipitation",
    "pressure_msl",
    "wind_speed_10m",
    "winddirection_10m"
  ])
  OM_CURRENT = f"is_day,{OM_HOURLY}"
  OM_DAILY = ",".join([
    "weathercode",
    "temperature_2m_min",
    "temperature_2m_max",
    "precipitation_sum",
    "precipitation_hours",
    "sunrise",
    "sunset"
  ])

  def __init__(self):
    self._url = "".join([
      "https://api.open-meteo.com/v1/forecast?",
      f"latitude={app_config.latitude}",
      f"&longitude={app_config.longitude}",
      "&wind_speed_unit=kmh",
      f"&current=is_day,{OpenMeteoDataProvider.OM_CURRENT}",
      f"&hourly={OpenMeteoDataProvider.OM_HOURLY}",
      f"&daily={OpenMeteoDataProvider.OM_DAILY}",
      "&timezone=auto",
      "&forecast_days=5"
      ])
    self._wifi   = None

    self.current = None
    self.hours   = []
    self.days    = []

  # --- set wifi-object   ----------------------------------------------------

  def set_wifi(self,wifi):
    """ set wifi-object """
    self._wifi   = wifi

  # --- parse iso-time   -----------------------------------------------------

  def _parse_time(self,tm):
    """ parse iso-timestamp """

    the_date, the_time = tm.split('T')
    year,month,mday    = the_date.split('-')
    hour               = the_time.split(':')[0]
    iso_pretty         = tm.replace('T',' ')
    return (the_date,the_time,year,month,mday,hour,iso_pretty)

  # --- parse current data   -------------------------------------------------

  def _parse_current(self,data):
    """ parse current data """

    self.current = Values()

    # parse current time
    tm                     = self._parse_time(data["time"])
    self.current.hour      = tm[5]
    self.current.day       = tm[4]
    self.current.month     = tm[3]
    self.current.update    = tm[6]

    # measurements
    self.current.temp       = data["temperature_2m"]
    self.current.is_day     = data["is_day"]
    self.current.wind_speed = data["wind_speed_10m"]
    self.current.wind_dir   = OpenMeteoDataProvider.DIRECTION[
      int((data["winddirection_10m"]+22.5)/45)]
    self.current.wmo       = data["weathercode"]

    #self.current.is_day    = data["is_day"]
    #self.current.pressure  = data["pressure_msl"]
    #self.current.humidity  = data["relativehumidity_2m"]
    #self.current.precipit  = data["precipitation"]

  # --- parse hourly data   --------------------------------------------------

  def _parse_hours(self,data):
    """ parse hourly data """

    # extract only a subset of hourly data:
    # three hours between 08:00 and 21:00

    h_now = int(self.current.hour)   # index into hour-data
    self._daily_off = 1              # offset into daily-data
    if h_now < 18:
      h_min = max(h_now+1,8)
      h_max = min(h_min+12,21)
      h_mid = int((h_min+h_max)/2)
    elif h_now < 21:
      h_min = h_now+1
      h_max = 23
      h_mid = int((h_min+h_max)/2)
    else:
      h_min   = 32   # 08:00 next day
      h_mid   = 38   # 14:00 next day
      h_max   = 44   # 20:00 next day
      self._daily_off = 2    # next day is already in hourly forecast

    for i in [h_min,h_mid,h_max]:
      val = Values()
      val.hour   = f"{i:02d}"
      val.temp   = data["temperature_2m"][i]
      val.wmo    = data["weathercode"][i]
      val.is_day = data["is_day"][i]
      #val.pressure  = data["pressure_msl"]
      #val.humidity  = data["relativehumidity_2m"]
      #val.precipit  = data["precipitation"]
      self.hours.append(val)

  # --- round data   ----------------------------------------------------------

  def _round(self,value):
    """ round data """
    if value > 0:
      return int((round(value*10,1)+5)/10)
    elif value < 0:
      return -int((round(-value*10,1)+5)/10)
    else:
      return value

  # --- get weekday   ---------------------------------------------------------

  def _get_wday(self,iso_t):
    """ get weekday from iso-day """

    y,m,d = iso_t.split("-")
    epoch = time.mktime((int(y),int(m),int(d),
                         12, 0, 0,
                         -1,-1,-1))
    return (int(epoch/86400)+3) % 7                    # 01/01/1970 is Thursday

  # --- parse daily data   ----------------------------------------------------

  def _parse_days(self,data):
    """ parse daily data """

    for i in range(self._daily_off,self._daily_off+4):
      val = Values()
      val.day   = data["time"][i][-2:]
      val.month = data["time"][i][-5:-3]
      val.wday  = self._get_wday(data["time"][i])
      val.tmin  = self._round(data["temperature_2m_min"][i])
      val.tmax  = self._round(data["temperature_2m_max"][i])
      val.wmo   = data["weathercode"][i]
      #val.sunrise    = self._parse_time(data["sunrise"])[1]
      #val.sunset     = self._parse_time(data["sunset"])[1]
      #val.prec_hours = data["precipitation_hours"]
      self.days.append(val)

  # --- query weather-data   -------------------------------------------------

  def update_data(self,data):
    """ callback for E-Ink-App: query weather data """

    om_data = self._wifi.get_json(self._url)

    # current: temp, wind-direction, wind-speed
    self._parse_current(om_data["current"])
    
    # next hours: hour, temp, wmo
    self._parse_hours(om_data["hourly"])

    # next days: date, temp (min/max), icon
    self._parse_days(om_data["daily"])

    #self.print_all()
    data.update({
      "units": {
        "temp":       om_data["current_units"]["temperature_2m"],
        "wind_speed": om_data["current_units"]["wind_speed_10m"]
        },
      "current": self.current,
      "hours":   self.hours,
      "days":    self.days
      })

  # --- print complete object   ----------------------------------------------

  def print_all(self):
    """ print complete object """

    print("Current:\n--------")
    self.current.print()
    print("-"*10)
    print("\nHours:\n-----")
    for hour in self.hours:
      hour.print()
      print("-"*10)
    print("\nDays:\n-----")
    for day in self.days:
      day.print()
      print("-"*10)
