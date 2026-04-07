import board

# Pins
PWM_OUT_PINS = [board.GP2,board.GP14]
POTENTIOMETER_AND_SWITCH_PINS = [(board.GP26_A0,board.GP18),(board.GP27_A1,board.GP19)]
INDICATOR_LIGHT_PIN = board.LED
NEOPIXEL_PIN = board.GP8

# Numbers of things
NUM_LIGHTS = 32
NUM_CHANNELS = 2  # NUM_CHANNELS should be a factor of NUM_LIGHTS
if NUM_CHANNELS > NUM_LIGHTS:
    raise

# Other specifications
DISPLAY_BRIGHTNESS = 0.1
PWM_FREQUENCY = 50
