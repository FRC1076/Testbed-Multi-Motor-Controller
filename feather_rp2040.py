import board

"""
Hardware specifications for the Double Wood Board testbed
"""

# Pins
PWM_OUT_PINS = [board.D24,board.D25]
POTENTIOMETER_AND_SWITCH_PINS = [(board.A0,board.D4),(board.A1,board.RX)]
INDICATOR_LIGHT_PIN = board.NEOPIXEL
NEOPIXEL_PIN = board.D6
# OLED_SCL_PIN = board.SCL0     # This is currently a placeholder
# OLED_SDA_PIN = board.SDA0     # This is currently a placeholder
MODE_SWITCH_PIN = board.D9

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
NEO_PIXEL_LIGHTS_ORDER = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
# OLED_DISPLAY_HEIGHT = 64
# OLED_DISPLAY_WIDTH = 128
