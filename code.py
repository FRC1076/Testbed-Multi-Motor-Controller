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

"""
This version is for the final, production product.
It includes two controls (LEFT and RIGHT).
Each side has a FORWARD/REVERSE toggle switch to specify the direction of the motor.
Contains a safety feature that displays the speed in a blinking error color if either motor is on at the start, and refuses to power the motors until the condition is corrected.
"""

# Colors
OFF = (0, 0, 0)
FORWARD_COLOR = (0, 255, 0)
REVERSE_COLOR = (255, 0, 0)
ERROR_COLOR = (255,127,0)
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
        self.light_state = 0
        if board.board_id == 'raspberry_pi_pico':
            self.indicator_pixel = digitalio.DigitalInOut(hw.INDICATOR_LIGHT_PIN)
            self.indicator_pixel.switch_to_output()
        elif board.board_id == 'adafruit_feather_rp2040':
            self.indicator_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=100)
    
    def update(self):
        self.cycle_count = (self.cycle_count + 1) % self.CYCLES_PER_TOGGLE
        if self.cycle_count == 0:
            if self.light_state:
                self.light_state = 0
                if board.board_id == 'adafruit_feather_rp2040':
                    self.indicator_pixel[0] = OFF
                elif board.board_id == 'adafruit_feather_rp2040':
                    self.indicator_pixel[0] = OFF
            else:
                self.light_state = 1
                if board.board_id == 'adafruit_feather_rp2040':
                    self.indicator_pixel[0] = PURPLE
                elif board.board_id == 'raspberry_pi_pico': 
                    self.indicator_pixel = self.light_state
        return self.light_state

# Object Creation
pixel_blinking = PixelBlinking()
CYCLE_TIME_ms = 20
cm = CycleManager(CYCLE_TIME_ms)

# Array creation
pwm = [None] * hw.NUM_CHANNELS
talon_speed_controller = [None] * hw.NUM_CHANNELS
speed_pin = [None] * hw.NUM_CHANNELS
direction_pin = [None] * hw.NUM_CHANNELS
direction_color = [None] * hw.NUM_CHANNELS
direction_sign = [None] * hw.NUM_CHANNELS
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

# Pixel initialization
pixels = neopixel.NeoPixel(hw.NEOPIXEL_PIN, hw.NUM_LIGHTS, brightness=hw.DISPLAY_BRIGHTNESS)
pixels.auto_write = False
pixels.fill(OFF)

# Make sure motors don't immediately start
non_zeros = check_for_nonzero_speed(speed_pin)
while len(non_zeros) != 0:
    cm.startCycle()
    
    # Pixel writing
    lights_state = pixel_blinking.update()
    pixels.fill(OFF)
    if lights_state:
        for channel in non_zeros:
            index[channel] = speed_to_index(speed_pin[channel].value)
            START_VAL = int(channel * (hw.NUM_LIGHTS / hw.NUM_CHANNELS))
            for i in range(START_VAL,index[channel]+START_VAL):
                pixels[hw.LIGHTS_ORDER[i]] = ERROR_COLOR
    
    pixels.show()
    non_zeros = check_for_nonzero_speed(speed_pin)
    cm.adjustCycle()

while True:
    cm.startCycle()
    
    # Running indicator flashing
    lights_state = pixel_blinking.update()
    indicator_pixel = lights_state
    
    # Pixel writing
    pixels.fill(OFF)
    for channel in range (hw.NUM_CHANNELS):
        # NeoFeather lights
        if direction_pin[channel].value:
            direction_sign[channel] = -1
            direction_color[channel] = REVERSE_COLOR
        else:
            direction_sign[channel] = 1
            direction_color[channel] = FORWARD_COLOR
        index[channel] = speed_to_index(speed_pin[channel].value)
        START_VAL = int(channel * (hw.NUM_LIGHTS / hw.NUM_CHANNELS))
        if index[channel] == 0:
            if lights_state:
                pixels[hw.LIGHTS_ORDER[START_VAL]] = direction_color[channel]
        else:
            for i in range(START_VAL,index[channel]+START_VAL):
                pixels[hw.LIGHTS_ORDER[i]] = direction_color[channel]
            
        # Motor code
        servo[channel] = speed_to_servo(speed_pin[channel].value)
        talon_speed_controller[channel].throttle = servo[channel] * direction_sign[channel]
        print("Servo",channel,":",servo[channel] * direction_sign[channel])
    
    pixels.show()
    cm.adjustCycle()
