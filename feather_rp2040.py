import board

"""
Hardware specifications for the Double Wood Board testbed.
"""

# Pins
MASTER_SWITCH_PIN = board.D9
PWM_OUT_PINS = [board.D24,board.D25]
POTENTIOMETER_AND_SWITCH_PINS = [(board.A0,board.D4),(board.A1,board.RX)]
NEOPIXEL_PIN = board.D6

# Numbers of things
NUM_LIGHTS = 32
NUM_CHANNELS = 2  # NUM_CHANNELS should be a factor of NUM_LIGHTS
if NUM_CHANNELS > NUM_LIGHTS:
    raise

# Other specifications
DISPLAY_BRIGHTNESS = 0.1
PWM_FREQUENCY = 50
LIGHTS_ORDER = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
