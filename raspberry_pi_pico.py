import board

"""
Hardware specifications
"""

# Pins
PWM_OUT_PINS = [board.GP14,board.GP2]
POTENTIOMETER_AND_SWITCH_PINS = [(board.GP26_A0,board.GP18),(board.GP27_A1,board.GP19)]
INDICATOR_LIGHT_PIN = board.LED
NEOPIXEL_PIN = board.GP22
OLED_SCL_PIN = board.GP9
OLED_SDA_PIN = board.GP8

PWM_FREQUENCY = 50

# Numbers of things
NUM_CHANNELS = 2  # NUM_CHANNELS should be a factor of NUM_LIGHTS
if NUM_CHANNELS > NUM_LIGHTS:
    raise

# Lights specs
DISPLAY_TYPES = ["OLED", "NEO_PIXEL"] # Current options are OLED and NEO_PIXEL

NEO_PIXEL_NUM_LIGHTS = 32
NEO_PIXEL_LIGHTS_ORDER = [28, 20, 12, 4, 29, 21, 13, 5, 30, 22, 14, 6, 31, 23, 15, 7, 24, 16, 8, 0, 25, 17, 9, 1, 26, 18, 10, 2, 27, 19, 11, 3]
OLED_DISPLAY_HEIGHT = 64
OLED_DISPLAY_WIDTH = 128
