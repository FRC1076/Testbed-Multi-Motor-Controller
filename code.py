import time
import board
import digitalio
import analogio
import neopixel

OFF = (0, 0, 0)
BLUE = (0, 0, 255)

indicator_pin = digitalio.DigitalInOut(board.GP15)
indicator_pin.direction = digitalio.Direction.OUTPUT

SPEED_PER_INDEX = 2000

def speed_to_index(speed):
    return speed // SPEED_PER_INDEX

speed_pin = analogio.AnalogIn(board.GP27)
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
    print("Speed: ", speed_pin.value)
    index = speed_to_index(speed_pin.value)
    print("Index: ", index)
    
    for i in range(index):
        pixels[i] = BLUE
        
    pixels.show()
