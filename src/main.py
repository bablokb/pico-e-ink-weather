# -------------------------------------------------------------------------
# Display weather-data (current and forecast) on an ACEP e-paper display.
#
# This program needs an additional configuration file secrets.py
# with wifi-credentials.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import time
start = time.monotonic()

from einkapp import EInkApp
from openmeteo_uiprovider   import OpenMeteoUIProvider   as UIProvider
from openmeteo_dataprovider import OpenMeteoDataProvider as DataProvider

ui_provider   = UIProvider()
data_provider = DataProvider() 
app = EInkApp(data_provider,ui_provider,with_rtc=True)
app.blink(0.5)
print(f"startup: {time.monotonic()-start:f}s")
app.run()
