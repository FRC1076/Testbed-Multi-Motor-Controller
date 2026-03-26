import board

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
