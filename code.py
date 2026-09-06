import time
import board
import digitalio
from CycleManager import CycleManager
import Display as disp
import Motor as drive

"""
This version is for the final, production product.
It includes two controls (LEFT and RIGHT).
Each side has a FORWARD/REVERSE toggle switch to specify the direction of the motor.
Contains a safety feature that displays the speed in a blinking error color if either motor is on at the start, and refuses to power the motors until the condition is corrected.
"""

# Object Creation
CYCLE_TIME_ms = 20
cm = CycleManager(CYCLE_TIME_ms)

# Mode switch
select_switch = digitalio.DigitalInOut(D_pin)
select_switch.direction = digitalio.Direction.INPUT
select_switch.pull = digitalio.Pull.UP

while True:
    # Mode selection
    while select_switch:
        cm.startCycle()
        mode_number = drive.motor.mode_select()
        disp.display.display_mode_select(mode_number)
        cm.adjustCycle()

    # Make sure motors don't immediately start
    speeds, non_zeros = drive.motor.check_for_nonzero_speed(speed_pin)

    while not select_switch and len(non_zeros) != 0:
        cm.startCycle()
        disp.display.display_error(mode_number, speeds, non_zeros)
        speeds, non_zeros = drive.motor.check_for_nonzero_speed(speed_pin)
        cm.adjustCycle()

    # Run the motors
    while not select_switch:
        cm.startCycle()
        speeds_and_directions = drive.motor.run_motor(mode_number)
        disp.display.display_speed(mode_number, speeds_and_directions)
        cm.adjustCycle()
