## ----------------------------------------------------------------------------
# esp32s3_pi_base_rev1.py: HAL for Waveshare-ESP32-S3-Pico
#                          and Inky-wHat/Impression
#
# N.B.: this uses a special CP-version with pin-mappings for the
#       picow_pi_base_rev2 board. The HAL-files are identical, because they
#       use Pi-names, the pins.c-file of the board-defintions map to the
#       actual pins of the MCU.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
#
# ----------------------------------------------------------------------------

from hal.picow_pi_base_rev1 import impl
