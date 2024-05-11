Display Open-Meteo Weatherdata on an E-Ink Display
==================================================

Overview
--------

This is a version of my project <https://github.com/bablokb/pi-e-ink-daily>
(for the display of weather-data) ported to CircuitPython.

Note that the intended target-system (Pico-W) fails with this
application, since it does not provide enough memory.
Instead, use a MCU with more memory, e.g. an
ESP32-S3. Maybe a future version of the Pico (RP2080??) might have
enough memory for this kind of application.

In contrast to the original project, this project uses Open-Meteo instead
of OpenWeatherMap as the source of weather-data.

While this specific project is about the display of weather-data,
the core of the software is content agnostic: it fetches data from a
server and then updates the display.


Installation
------------

To install the software, the following steps are necessary:

  1. Install the current version of CircuitPython on the device
  2. Copy all files *below* `src/` to the `CIRCUITPY`-drive
  3. Install circup: `pip3 install circup`
  4. Run `circup --path=path-to-your-device install -r requirements.txt`
  5. Add a file `settings.py` to your `CIRCUITPY`-drive (see next section)

Depending on your e-ink display, additional libraries might be necessary.


Software-Configuration
----------------------

The application needs a configuration file `settings.py`. This file is
*not* maintained in the repository since it is specific to the user
environment.

 The `settings.py`-file configures

  - network credentials (WLAN-SSID, password)
  - hardware (if not board-specific, see below)
  - UI-attributes (if different to the defaults in `ui_settings.py`)
  - application settings (location-coordinates for weather)

The project provides a sample settings-file in `src/settings_template.py`.
Copy this file to `settings.py` and adapt it to your specific situation.


Hardware Configuration
----------------------

From a hardware perspective, the application uses a display and nothing
else. 

To port the program to a different device and/or hardware combination,
you need to define the hardware of the MCU development board, in this
case only the display:

  - create a file `src/hal/<board.board_id>.py` with board-specific
    implementations and/or
  - add the relevant function for the display to `settings.py`

To lookup `board.board_id`, start the REPL and run:

    import board
    print(board.board_id)

Use one of the existing files in `src/hal` as a blueprint for your board.

You should define hardware that is not hard-wired to the dev-board
in `settings.py`.

As an example, consider a Feather ESP32-S3 with an attached SPI-display.

In this case, the hal-file would be
`src/hal/adafruit_feather_esp32s3_4mbflash_2mbpsram.py`.
Since this board does not define any specific hardware, the hal-file
is actually not necessary since the system will use sensible defaults
if it does not find a specific hal-file.

In this example, the definition of the display should go into the
file `settings.py`, e.g.:

    hw_config = Settings()

    def _get_display():
      import board
      import displayio
      import busio
      from adafruit_st7735r import ST7735R
      displayio.release_displays()
      spi = busio.SPI(clock=board.GP10,MOSI=board.GP11)
      bus = displayio.FourWire(spi,command=board.GP8,chip_select=board.GP9,
                               reset=board.GP12)
      return ST7735R(bus,width=180,height=80,
                              colstart=28,rowstart=0,invert=True,
                              rotation=90,bgr=True)

    hw_config.DISPLAY     = _get_display
