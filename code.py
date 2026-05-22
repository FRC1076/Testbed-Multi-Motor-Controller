import time
import board
import digitalio
import analogio
import neopixel
import pwmio
from CycleManager import CycleManager
from adafruit_motor import servo as adafruit_servo
if board.board_id == 'raspberry_pi_pico':
    import raspberry_pi_pico as hw
elif board.board_id == 'adafruit_feather_rp2040':
    import feather_rp2040 as hw
from Display import FullDisplay, PixelBlinking, OLEDDisplay, NEOPixelDisplay, UARTDisplay

"""
This version is for the final, production product.
It includes two controls (LEFT and RIGHT).
Each side has a FORWARD/REVERSE toggle switch to specify the direction of the motor.
Contains a safety feature that displays the speed in a blinking error color if either motor is on at the start, and refuses to power the motors until the condition is corrected.
"""

# Functions
SERVO_PER_SPEED = 65535.0
DEADBAND = 0.01

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

# Object Creation
CYCLE_TIME_ms = 20
cm = CycleManager(CYCLE_TIME_ms)
display = FullDisplay(PixelBlinking, OLEDDisplay, NEOPixelDisplay, UARTDisplay, hw)

# Array creation
pwm = [None] * hw.NUM_CHANNELS
talon_speed_controller = [None] * hw.NUM_CHANNELS
speed_pin = [None] * hw.NUM_CHANNELS
direction_pin = [None] * hw.NUM_CHANNELS
direction_sign = [None] * hw.NUM_CHANNELS
servos_and_directions = [None] * hw.NUM_CHANNELS
servo = [None] * hw.NUM_CHANNELS
index = [None] * hw.NUM_CHANNELS

# PWM Creation
for (channel,pin) in enumerate(hw.PWM_OUT_PINS):
    pwm[channel] = pwmio.PWMOut(pin,frequency=hw.PWM_FREQUENCY)
    talon_speed_controller[channel] = adafruit_servo.ContinuousServo(pwm[channel])

# Speed and Direction pin creation
for (channel,(A_pin,D_pin)) in enumerate(hw.POTENTIOMETER_AND_SWITCH_PINS):
    speed_pin[channel] = analogio.AnalogIn(A_pin)
    direction_pin[channel] = digitalio.DigitalInOut(D_pin)
    direction_pin[channel].direction = digitalio.Direction.INPUT
    direction_pin[channel].pull = digitalio.Pull.UP

# Make sure motors don't immediately start
non_zeros = check_for_nonzero_speed(speed_pin)
while len(non_zeros) != 0:
    cm.startCycle()

    for channel in range (hw.NUM_CHANNELS):        
        servo[channel] = speed_to_servo(speed_pin[channel].value)
    display.display_error(servo, non_zeros)
    non_zeros = check_for_nonzero_speed(speed_pin)
    cm.adjustCycle()

while True:
    cm.startCycle()
    
    # Motor code
    for channel in range (hw.NUM_CHANNELS):        
        if direction_pin[channel].value:
            direction_sign = -1
        else:
            direction_sign = 1
        servo = speed_to_servo(speed_pin[channel].value)
        talon_speed_controller[channel].throttle = servo * direction_sign
        
        servos_and_directions[channel] = (servo, direction_sign)
    display.display_speed(servos_and_directions)
    
    cm.adjustCycle()
