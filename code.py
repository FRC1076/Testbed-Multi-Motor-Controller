import time
import board
import digitalio
import analogio
import neopixel
import pwmio
from adafruit_motor import servo as adafruit_servo
if board.board_id == 'adafruit_feather_rp2040':
    import feather_rp2040 as hw

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
SPEED_PER_INDEX = 8000/hw.NUM_CHANNELS
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
    for channel in range(hw.NUM_CHANNELS):
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
        self.CYCLES_PER_TOGGLE = 10
        self.cycle_count = 0
        self.indicator_color = OFF
        self.light_state = 0

    def update(self):
        self.cycle_count = (self.cycle_count + 1) % self.CYCLES_PER_TOGGLE
        if self.cycle_count == 0:
            if self.light_state:
                self.indicator_color = OFF
                self.light_state = 0
            else:
                self.indicator_color = PURPLE
                self.light_state = 1
        return self.indicator_color, self.light_state
pixel_blinking = PixelBlinking()

# Array creation
pwm = [None] * hw.NUM_CHANNELS
talon_speed_controller = [None] * hw.NUM_CHANNELS
speed_pin = [None] * hw.NUM_CHANNELS
direction_pin = [None] * hw.NUM_CHANNELS
direction_color = [None] * hw.NUM_CHANNELS
direction_sign = [None] * hw.NUM_CHANNELS
servo = [None] * hw.NUM_CHANNELS
index = [None] * hw.NUM_CHANNELS

# Master Switch initialization
master_switch = digitalio.DigitalInOut(hw.MASTER_SWITCH_PIN)
master_switch.direction = digitalio.Direction.INPUT
master_switch.pull = digitalio.Pull.UP

# PWM Creation
for (channel,pin) in enumerate(hw.PWM_OUT_PINS):
    pwm[channel] = pwmio.PWMOut(pin,frequency=50)
    talon_speed_controller[channel] = adafruit_servo.ContinuousServo(pwm[channel])

# Speed and Direction pin creation
for (channel,(A_pin,D_pin)) in enumerate(hw.POTENTIOMETER_AND_SWITCH_PINS):
    speed_pin[channel] = analogio.AnalogIn(A_pin)
    direction_pin[channel] = digitalio.DigitalInOut(D_pin)
    direction_pin[channel].direction = digitalio.Direction.INPUT
    direction_pin[channel].pull = digitalio.Pull.UP

# Pixel writing part 1/2
pixels = neopixel.NeoPixel(hw.NEOPIXEL_PIN, 32, brightness=0.1)
pixels.auto_write = False
pixels.fill(OFF)

#Running indicator initialization
indicator_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=100)

# Make sure motors don't immediately start
non_zeros = check_for_nonzero_speed(speed_pin)
while len(non_zeros) != 0:
    # Running indicator flashing
    indicator_color, lights_state = pixel_blinking.update()
    indicator_pixel[0] = indicator_color
    
    pixels.fill(OFF)
    if lights_state:
        for channel in non_zeros:
            index[channel] = speed_to_index(speed_pin[channel].value)
            START_VAL = int(channel * (hw.NUM_LIGHTS / hw.NUM_CHANNELS))
            for i in range(START_VAL,index[channel]+START_VAL):
                pixels[i] = ORANGE
    
    pixels.show()
    time.sleep(0.02)
    non_zeros = check_for_nonzero_speed(speed_pin)

while True:
    # Running indicator flashing
    indicator_color, lights_state = pixel_blinking.update()
    indicator_pixel[0] = indicator_color
    
    # Pixel writing part 2/2
    pixels.fill(OFF)
    for channel in range (hw.NUM_CHANNELS):
        # NeoFeather lights
        if direction_pin[channel].value:
            direction_sign[channel] = -1
            direction_color[channel] = RED
        else:
            direction_sign[channel] = 1
            direction_color[channel] = GREEN
        index[channel] = speed_to_index(speed_pin[channel].value)
        START_VAL = int(channel * (hw.NUM_LIGHTS / hw.NUM_CHANNELS))
        if index[channel] == 0:
            if lights_state:
                pixel[START_VAL] = direction_color[channel]
        else:
            for i in range(START_VAL,index[channel]+START_VAL):
                pixels[i] = direction_color[channel]
            
        # Motor code
        if master_switch.value:
            servo[channel] = speed_to_servo(speed_pin[channel].value)
        else:
            servo[channel] = 0
        talon_speed_controller[channel].throttle = servo[channel] * direction_sign[channel]
        if master_switch.value:
            print("Servo",channel,":",servo[channel] * direction_sign[channel])
        else:
            print("Master Switch Off")

    pixels.show()
    time.sleep(0.02)
