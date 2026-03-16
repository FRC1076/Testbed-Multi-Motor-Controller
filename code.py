import time
import board
import digitalio
import analogio
import neopixel
import pwmio
from adafruit_motor import servo as adafruit_servo

"""
This version is for the second (woody) prototype using an RPi Feather.
It includes two controls (LEFT and RIGHT).
A MASTER button determines whether or not the motors are running or not.
Each side has a FORWARD/REVERSE toggle switch to specify the direction of the motor.
"""

# Colors
OFF = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (120, 0, 120)

# Functions
SPEED_PER_INDEX = 4000
SERVO_PER_SPEED = 65535.0
DEADBAND = 0.01

def speed_to_index(speed):
    """
    Convert the raw speed value into pixel index
    """
    return speed // SPEED_PER_INDEX

def speed_to_servo(speed):
    """
    Convert raw speed to servo control speed subject to DEADBAND
    """
    servo = speed / SERVO_PER_SPEED
    if abs(servo) < DEADBAND:
        return 0.0
    else:
        return servo

# Controller Pins
MASTER_SWITCH_PIN = board.D9
PWM_PINS = [board.D24,board.D25]
ANALOG_PINS = [(board.A0,board.D4),(board.A1,board.RX)]
NEOPIXEL_PIN = board.D6

# Array creation
NUM_CHANNELS = 2**1  # NUM_CHANNELS should be a power of 2, or things get weird.
if NUM_CHANNELS > 32:
    raise
pwm = [None] * NUM_CHANNELS
talon_speed_controller = [None] * NUM_CHANNELS
speed_pin = [None] * NUM_CHANNELS
direction_pin = [None] * NUM_CHANNELS
direction_color = [None] * NUM_CHANNELS
direction_sign = [None] * NUM_CHANNELS
servo = [None] * NUM_CHANNELS
index = [None] * NUM_CHANNELS

# Master Switch initialization
master_switch = digitalio.DigitalInOut(MASTER_SWITCH_PIN)
master_switch.direction = digitalio.Direction.INPUT
master_switch.pull = digitalio.Pull.UP

# PWM Creation
for (channel,pin) in enumerate(PWM_PINS):
    pwm[channel] = pwmio.PWMOut(pin,frequency=50)
    talon_speed_controller[channel] = adafruit_servo.ContinuousServo(pwm[channel])

# Speed and Direction pin creation
for (channel,(A_pin,D_pin)) in enumerate(ANALOG_PINS):
    speed_pin[channel] = analogio.AnalogIn(A_pin)
    direction_pin[channel] = digitalio.DigitalInOut(D_pin)
    direction_pin[channel].direction = digitalio.Direction.INPUT
    direction_pin[channel].pull = digitalio.Pull.UP

# Pixel writing and Motors below
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, 32, brightness=0.1)
pixels.auto_write = False
pixels.fill(OFF)

#Running indicator initialization
indicator_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=100)

while True:
    # Running indicator flashing
    indicator_pixel[0] = PURPLE
    time.sleep(0.1)
    indicator_pixel[0] = OFF
    time.sleep(0.1)
    
    pixels.fill(OFF)
    for channel in range (NUM_CHANNELS):
        # NeoFeather lights
        if direction_pin[channel].value:
            direction_sign[channel] = -1
            direction_color[channel] = RED
        else:
            direction_sign[channel] = 1
            direction_color[channel] = GREEN
        index[channel] = speed_to_index(speed_pin[channel].value)
        START_VAL = int(channel*32/NUM_CHANNELS)
        for i in range(START_VAL,index[channel]+START_VAL):
            pixels[i] = direction_color[channel]
            
        # Motor code
        if master_switch.value:
            servo[channel] = speed_to_servo(speed_pin[channel].value)
        else:
            servo[channel] = 0
        talon_speed_controller[channel].throttle = servo[channel] * direction_sign[channel]
        print("Servo",channel,":",servo[channel] * direction_sign[channel])

    pixels.show()
