import time
import board
import digitalio
import analogio
import neopixel
import pwmio
from adafruit_motor import servo as adafruit_servo

"""
This version is for the second (woody) prototype using an RPi Feather.
It includes two controls (LEFT and RIGHT). A MASTER button determines whether or not the motors are running or not.
Each side has a FORWARD/REVERSE toggle switch to specify the direction of the motor.
Contains a safety feature that displays the speed in blinking orange if either motor is on at the start, 
and refuses to power the motors until the condition is corrected.
"""

# Colors
OFF = (0, 0, 0)
ORANGE = (255,63,0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (120, 0, 120)

# Functions
NUM_CHANNELS = 2**1  # NUM_CHANNELS should be a power of 2, or things get weird.
if NUM_CHANNELS > 32:
    raise
SPEED_PER_INDEX = 8000/NUM_CHANNELS
SERVO_PER_SPEED = 65535.0
DEADBAND = 0.01

def speed_to_index(speed):
    """
    Convert the raw speed value into pixel index
    """
    return speed // SPEED_PER_INDEX

def check_for_nonzero_speed(speed_pins):
    """
    See if any pins are on
    """
    non_zeros = [ ]
    for channel in range(NUM_CHANNELS):
        pins = speed_to_servo(speed_pins[channel].value)
        if pins > DEADBAND:
            non_zeros.append(channel)
    return non_zeros

def speed_to_servo(speed):
    """
    Convert raw speed to servo control speed subject to DEADBAND
    """
    servo = speed / SERVO_PER_SPEED
    if abs(servo) < DEADBAND:
        return 0.0
    else:
        return servo

class PixelBlinking:
    """
    Make pixels blink while not slowing cycles
    """
    def __init__ (self):
        self.CYCLES_PER_TOGGLE = 25
        self.cycle_count = 0
        self.indicator_color = OFF
        self.error_color = OFF

    def update(self):
        self.cycle_count = (self.cycle_count + 1) % self.CYCLES_PER_TOGGLE
        if self.cycle_count == 0:
            if self.indicator_color == OFF:
                self.indicator_color = PURPLE
                self.error_color = ORANGE
            else:
                self.indicator_color = OFF
                self.error_color = OFF
        return self.indicator_color, self.error_color
pixel_blinking = PixelBlinking()

# Controller Pins
MASTER_SWITCH_PIN = board.D9
PWM_PINS = [board.D24,board.D25]
ANALOG_PINS = [(board.A0,board.D4),(board.A1,board.RX)]
NEOPIXEL_PIN = board.D6

# Array creation. See NUM_CHANNELS above in Functions
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

# Pixel writing part 1/2
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, 32, brightness=0.1)
pixels.auto_write = False
pixels.fill(OFF)

#Running indicator initialization
indicator_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=100)

# Make sure motors don't immediately start
non_zeros = check_for_nonzero_speed(speed_pin)
while len(non_zeros) != 0:
    # Running indicator flashing
    indicator_color, error_color = pixel_blinking.update()
    indicator_pixel[0] = indicator_color

    pixels.fill(OFF)
    for channel in non_zeros:
        index[channel] = speed_to_index(speed_pin[channel].value)
        START_VAL = int(channel*32/NUM_CHANNELS)
        for i in range(START_VAL,index[channel]+START_VAL):
            pixels[i] = error_color
            
    pixels.show()
    time.sleep(0.02)
    non_zeros = check_for_nonzero_speed(speed_pin)

while True:
    # Running indicator flashing
    indicator_color, error_color = pixel_blinking.update()
    indicator_pixel[0] = indicator_color
    
    # Pixel writing part 2/2
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
    time.sleep(0.02)