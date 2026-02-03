import time
import board
import digitalio
import analogio
import neopixel
import pwmio
from adafruit_motor import servo

"""
This version is for second(woody) prototype using RPi Feather.
It includes two controls (LEFT, and RIGHT).
A MASTER button determines whether or not the two motors are controlled by the same, or if the controls are separate.
Each side has a FORWARD/REVERSE toggle switch to specify the direction of the motor.
"""

OFF = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (120, 0, 120)

indicator_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=100)

#indicator_pin = digitalio.DigitalInOut(board.GP15)
#indicator_pin.direction = digitalio.Direction.OUTPUT

pwm = pwmio.PWMOut(board.D12, frequency=50)
talon_speed_controller = servo.ContinuousServo(pwm)

SPEED_PER_INDEX = 4000
SERVO_PER_SPEED = 65535.0
DEADBAND = 0.01

def speed_to_index(speed):
    return speed // SPEED_PER_INDEX
    
def speed_to_servo(speed):
    servo = speed / SERVO_PER_SPEED
    if abs(servo) < DEADBAND:
        return 0.0
    else:
        return servo

speed_pin = analogio.AnalogIn(board.A0)
direction_pin = digitalio.DigitalInOut(board.D10)
direction_pin.direction = digitalio.Direction.INPUT
direction_pin.pull = digitalio.Pull.UP


#speed_pin.direction = analogio.AnalogIn

pixels = neopixel.NeoPixel(board.D6, 32, brightness=0.1)

pixels.auto_write = False
pixels.fill(OFF)

while True:
    indicator_pixel[0] = PURPLE
    time.sleep(0.1)
    indicator_pixel[0] = OFF
    time.sleep(0.1)

    pixels.fill(OFF)
    #print("Speed: ", speed_pin.value)
    index = speed_to_index(speed_pin.value)
    #print("Index: ", index)
    #print("*" * index)

    if direction_pin.value:
        direction_sign = 1
        direction_color = GREEN
    else:
        direction_sign = -1
        direction_color = RED
        
    servo = speed_to_servo(speed_pin.value)
    #print("Servo: ", servo)
    talon_speed_controller.throttle = servo * direction_sign
    
    for i in range(index):
        pixels[i] = direction_color
        
    for i in range(16, index+16):
        pixels[i] = RED

    pixels.show()





