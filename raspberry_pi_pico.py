import board

# Pins
PWM_OUT_PINS = [board.PWM0A,board.PWM7A]
POTENTIOMETER_AND_SWITCH_PINS = [(board.GP26_A0,board.GP18),(board.AGP27_A1,board.GP19)]
INDICATOR_LIGHT_PIN = board.LED

# Numbers of things
NUM_LIGHTS = 32
NUM_CHANNELS = 2  # NUM_CHANNELS should be a factor of NUM_LIGHTS
if NUM_CHANNELS > NUM_LIGHTS:
    raise

# Other specifications
DISPLAY_BRIGHTNESS = 0.1
PWM_FREQUENCY = 50
