import board

"""
Hardware specifications for the first version of the final product.
"""

# Pins
PWM_OUT_PINS = [board.GP14,board.GP2]
POTENTIOMETER_AND_SWITCH_PINS = [(board.GP26_A0,board.GP18),(board.GP27_A1,board.GP19)]
INDICATOR_LIGHT_PIN = board.LED
NEOPIXEL_PIN = board.GP22

# Numbers of things
NUM_LIGHTS = 32
NUM_CHANNELS = 2  # NUM_CHANNELS should be a factor of NUM_LIGHTS
if NUM_CHANNELS > NUM_LIGHTS:
    raise

# Other specifications
DISPLAY_BRIGHTNESS = 0.025
PWM_FREQUENCY = 50
LIGHTS_ORDER = [28, 20, 12, 4, 29, 21, 13, 5, 30, 22, 14, 6, 31, 23, 15, 7, 24, 16, 8, 0, 25, 17, 9, 1, 26, 18, 10, 2, 27, 19, 11, 3]
