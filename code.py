import time
import board
import digitalio
from CycleManager import CycleManager
if board.board_id == 'raspberry_pi_pico':
    import raspberry_pi_pico as hw
elif board.board_id == 'adafruit_feather_rp2040':
    import feather_rp2040 as hw
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
select_switch = digitalio.DigitalInOut(hw.MODE_SWITCH_PIN)
select_switch.direction = digitalio.Direction.INPUT
select_switch.pull = digitalio.Pull.UP

# Carried variables
mode_number = 0

while True:
    # Mode selection
    while select_switch.value:
        cm.startCycle()
        mode_number = drive.motor.mode_select()
        disp.display.display_mode_select(mode_number)
        cm.adjustCycle()

    # Make sure motors don't immediately start
    speeds, non_zeros = drive.motor.check_for_nonzero_speed()

    while not select_switch.value and len(non_zeros) != 0:
        cm.startCycle()
        disp.display.display_error(mode_number, speeds, non_zeros)
        speeds, non_zeros = drive.motor.check_for_nonzero_speed()
        cm.adjustCycle()

    # Run the motors
    while not select_switch.value:
        cm.startCycle()
        speeds_and_directions = drive.motor.run_motor()
        disp.display.display_speed(mode_number, speeds_and_directions)
        cm.adjustCycle()
