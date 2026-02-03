import time
import board
import digitalio
import analogio
import neopixel
import pwmio
from adafruit_motor import servo

"""
This code works on raspberry pi pico breadboard prototype, for a single motor control.
"""

OFF = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

indicator_pin = digitalio.DigitalInOut(board.GP15)
indicator_pin.direction = digitalio.Direction.OUTPUT

pwm = pwmio.PWMOut(board.GP18, frequency=50)
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

speed_pin = analogio.AnalogIn(board.GP27)
direction_pin = digitalio.DigitalInOut(board.GP22)
direction_pin.direction = digitalio.Direction.INPUT
direction_pin.pull = digitalio.Pull.UP


#speed_pin.direction = analogio.AnalogIn

pixels = neopixel.NeoPixel(board.GP16, 32, brightness=0.1)

print("Pin is configured")
print("Pin is set to ", indicator_pin.direction)

pixels.auto_write = False
pixels.fill(OFF)

while True:
    indicator_pin.value = True
    time.sleep(0.1)
    indicator_pin.value = False
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
    print("Servo: ", servo)
    talon_speed_controller.throttle = servo * direction_sign
    
    for i in range(index):
        pixels[i] = direction_color
        
    for i in range(16, index+16):
        pixels[i] = RED

    pixels.show()



