import board

"""
Hardware specifications
"""

# Pins
PWM_OUT_PINS = [board.GP2,board.GP14]
POTENTIOMETER_AND_SWITCH_PINS = [(board.GP27_A1,board.GP19),(board.GP26_A0,board.GP18)]
INDICATOR_LIGHT_PIN = board.LED
NEOPIXEL_PIN = board.GP22
OLED_SCL_PIN = board.GP9
OLED_SDA_PIN = board.GP8
MODE_SWITCH_PIN = board.GP11       # Placeholder

PWM_FREQUENCY = 50

# Hardware Configuration that I thought more sense here than in Config
BASE_CHANNEL = 0
DEADBAND = 0.01

# Numbers of things
NUM_CHANNELS = 2 

# Lights specs
DISPLAY_TYPES = ["NEO_PIXEL"] # Current options are OLED and NEO_PIXEL

NEO_PIXEL_NUM_LIGHTS = 32
if NUM_CHANNELS > NEO_PIXEL_NUM_LIGHTS:
    raise       # You can’t display info on all channels if you don’t have at least one light per channel
NEO_PIXEL_LIGHTS_ORDER = [24, 16, 8, 0, 25, 17, 9, 1, 26, 18, 10, 2, 27, 19, 11, 3, 28, 20, 12, 4, 29, 21, 13, 5, 30, 22, 14, 6, 31, 23, 15, 7]
OLED_DISPLAY_HEIGHT = 64
OLED_DISPLAY_WIDTH = 128
