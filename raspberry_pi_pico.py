import board

"""
Hardware specifications for the first version of the final product.
"""

# Pins
PWM_OUT_PINS = [board.GP14,board.GP2]
POTENTIOMETER_AND_SWITCH_PINS = [(board.GP26_A0,board.GP18),(board.GP27_A1,board.GP19)]
INDICATOR_LIGHT_PIN = board.LED
NEOPIXEL_PIN = board.GP22

PWM_FREQUENCY = 50

# Numbers of things
NUM_LIGHTS = 32
NUM_CHANNELS = 2  # NUM_CHANNELS should be a factor of NUM_LIGHTS
if NUM_CHANNELS > NUM_LIGHTS:
    raise

# Lights specs
# OLED_VERTICALS = [24, 40, 52] # Verticals for direction text, speed text, and speed bar respectively
# OLED_HORIZONTALS = [4,68]
# OLED_DISPLAY_HEIGHT = 64
# OLED_DISPLAY_WIDTH = 128
# OLED_BAR_WIDTH = 56
DISPLAY_TYPES = ["NEO_PIXEL", "UART"] # Current options are OLED, NEO_PIXEL, UART
NEO_PIXEL_DISPLAY_BRIGHTNESS = 0.025
NEO_PIXEL_LIGHTS_ORDER = [28, 20, 12, 4, 29, 21, 13, 5, 30, 22, 14, 6, 31, 23, 15, 7, 24, 16, 8, 0, 25, 17, 9, 1, 26, 18, 10, 2, 27, 19, 11, 3]
