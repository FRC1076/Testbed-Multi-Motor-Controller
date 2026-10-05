import board
import digitalio
import analogio
import pwmio
from adafruit_motor import servo as adafruit_servo
if board.board_id == 'raspberry_pi_pico':
    import raspberry_pi_pico as hw
elif board.board_id == 'adafruit_feather_rp2040':
    import feather_rp2040 as hw
import config as cfg

class DriveMotor:    
    def __init__(self, hw, cfg):
        self.hw = hw
        self.modes = cfg.modes

        # Constants and carried variables
        self.SERVO_PER_POTENTIOMETER = 65535.0
        self.mode_number = 0

        # Array creation
        self.talon_speed_controller = [None] * hw.NUM_CHANNELS
        self.speed = [None] * hw.NUM_CHANNELS
        self.direction_pin = [None] * hw.NUM_CHANNELS
        self.direction_signs = [0] * hw.NUM_CHANNELS
        self.speeds_and_directions = [None] * hw.NUM_CHANNELS
        
        for (channel,pin) in enumerate(hw.PWM_OUT_PINS):
            self.talon_speed_controller[channel] = adafruit_servo.ContinuousServo(pwmio.PWMOut(pin,frequency=hw.PWM_FREQUENCY))
        for (channel,(A_pin,D_pin)) in enumerate(hw.POTENTIOMETER_AND_SWITCH_PINS):
            self.speed[channel] = self.potentiometer_to_speed(analogio.AnalogIn(A_pin).value)
            self.direction_pin[channel] = digitalio.DigitalInOut(D_pin)
            self.direction_pin[channel].direction = digitalio.Direction.INPUT
            self.direction_pin[channel].pull = digitalio.Pull.UP

    def mode_select(self):
        if self.direction_pin[self.hw.BASE_CHANNEL].value:
            if self.direction_pin[self.hw.BASE_CHANNEL + 1].value:
                self.mode_number = 0
            else:
                self.mode_number = 1
        else:
            if self.direction_pin[self.hw.BASE_CHANNEL + 1].value:
                self.mode_number = 2
            else:
                self.mode_number = 3
        return self.mode_number

    def potentiometer_to_speed(self, potentiometer):
        """
        Convert raw speed to servo control speed subject to DEADBAND
        """
        speed = potentiometer / self.SERVO_PER_POTENTIOMETER
        if abs(speed) < self.hw.DEADBAND:
            return 0.0
        else:
            return speed

    def make_speeds_and_directions(self, error_state=False):
        if error_state:
            for (channel, direction) in enumerate(self.direction_signs):
                self.speeds_and_directions[channel] = (self.speed[channel], 1)
        else:
            if f"{self.modes[self.mode_number]}" == "same_speed":
               for (channel, direction) in enumerate(self.direction_signs): 
                    self.speeds_and_directions[channel] = (self.speed[self.hw.BASE_CHANNEL], direction)
            elif f"{self.modes[self.mode_number]}" == "separate_speeds":
               for (channel, direction) in enumerate(self.direction_signs): 
                    self.speeds_and_directions[channel] = (self.speed[channel], direction)

    def check_for_nonzero_speed(self):
        """
        See if any pins are on
        """
        non_zeros = [ ]
        if f"{self.modes[self.mode_number]}" == "same_speed":
            if self.speed[self.hw.BASE_CHANNEL] > self.hw.DEADBAND:
                non_zeros.append(self.hw.BASE_CHANNEL)
        else:
            for channel in range(self.hw.NUM_CHANNELS):
                if self.speed[channel] > self.hw.DEADBAND:
                    non_zeros.append(channel)
        self.make_speeds_and_directions(error_state=True)
        return self.speeds_and_directions, non_zeros

    def separate_speed(self):
        for channel in range(len(self.direction_signs)):
            self.talon_speed_controller[channel] = self.speed[channel] * self.direction_signs[channel]

    def same_speed(self):
        for (channel, direction) in enumerate(self.direction_signs):
            self.talon_speed_controller[channel] = self.speed[self.hw.BASE_CHANNEL] * direction

    def run_motor(self):
        for channel in range (self.hw.NUM_CHANNELS):
            if self.direction_pin[channel].value:
                self.direction_signs[channel] = -1
            else:
                self.direction_signs[channel] = 1
            
            if self.modes[self.mode_number] == "separate_speed":
                self.separate_speed()
            elif self.modes[self.mode_number] == "same_speed":
                self.same_speed()
            elif self.modes[self.mode_number] == "no_speed":
                self.no_speed()
        self.make_speeds_and_directions()
        return self.speeds_and_directions
motor = DriveMotor(hw, cfg)
