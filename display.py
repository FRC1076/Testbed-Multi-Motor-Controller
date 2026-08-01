import board
import displayio
import terminalio
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus
import busio
import neopixel
import adafruit_displayio_ssd1306
if board.board_id == 'raspberry_pi_pico':
    import raspberry_pi_pico as hw
    import digitalio
elif board.board_id == 'adafruit_feather_rp2040':
    import feather_rp2040 as hw
import display_config as cfg

class IndicatorLight:
    def __init__(self, hw, pi_pico=True, cycles_per_toggle=10):
        # This is set up to be a base class and to work on a Pi Pico.
        self.cycle_count = 0
        self.CYCLES_PER_BLINK = cycles_per_toggle
        self.light_state = False
        if pi_pico:
            self.indicator_pixel = digitalio.DigitalInOut(hw.INDICATOR_LIGHT_PIN)
            self.indicator_pixel.switch_to_output()
            
    def update_light(self, light_state):
        self.indicator_pixel.value = light_state

    def show_on(self):
        self.cycle_count = (self.cycle_count + 1) % self.CYCLES_PER_BLINK
        if self.cycle_count == 0:
            self.light_state = not self.light_state
            if self.light_state:
                self.update_light(True)
            else:
                self.update_light(False)

class FeatherIndicatorLight(IndicatorLight):
    def __init__(self, hw):
        super().__init__(hw, pi_pico=False)
        self.indicator_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=100)
        self.ON = (127, 0, 127) # Purple
        self.OFF = (0,0,0)

    def update_light(self, light_state):
        if light_state:
            COLOR = self.ON
        else:
            COLOR = self.OFF
        self.indicator_pixel[0] = COLOR

# Indicator Light Factory
if board.board_id == 'raspberry_pi_pico':
    indicator = IndicatorLight(hw)
elif board.board_id == 'adafruit_feather_rp2040':
    indicator = FeatherIndicatorLight(hw)

class Display:
    def __init__(self, logging=False, blinking=False, cycles_per_toggle=10):
        self.logging = logging
        self.blinking = blinking
        if self.blinking:
            self.CYCLES_PER_BLINK = cycles_per_toggle
            self.cycle_count = 0
            self.light_state = False
            print("Blinking on")
            print("Cycles per toggle:", cycles_per_toggle) 
    
    def update_blink(self):
        if self.blinking:
            self.cycle_count = (self.cycle_count + 1) % self.CYCLES_PER_BLINK
            if self.cycle_count == 0:
                self.light_state = not self.light_state
            return self.light_state
        else:
            print("Blinking off")
            return 0

    def log_error(self, non_zeros):
        if self.logging:
           print("Set Servo(s)", non_zeros, "to zero to start.")

    def log_speed(self, speeds_and_directions):
        if self.logging:
            for (channel, (speed, direction)) in enumerate(speeds_and_directions):
                print(f"Servo {channel}: {speed * direction}")

    def print_error(self, speeds, non_zeros):
        self.log_error(non_zeros)

    def print_speed(self, speeds_and_directions):
        self.log_speed(speeds_and_directions)

class NEOPixelDisplay(Display):
    def __init__(self, hw, cfg, logging):
        super().__init__(logging, True)

        # Colors
        self.hw = hw
        self.cfg = cfg
        self.OFF = (0, 0, 0)

        # Display init
        self.pixels = neopixel.NeoPixel(hw.NEOPIXEL_PIN, hw.NEO_PIXEL_NUM_LIGHTS, brightness=cfg.NEO_PIXEL_DISPLAY_BRIGHTNESS)
        self.pixels.auto_write = False
        self.pixels.fill(self.OFF)

    def speed_to_index(self, speed):
        """
        Convert the speed percentage into pixel index
        """
        return speed * self.hw.NEO_PIXEL_NUM_LIGHTS / self.hw.NUM_CHANNELS

    def start_val(self, channel):
        """
        Calculate start value for the display
        """
        return int(channel * (self.hw.NEO_PIXEL_NUM_LIGHTS / self.hw.NUM_CHANNELS))

    def print_error(self, speeds, non_zeros):
        self.log_error(non_zeros)
        self.pixels.fill(self.OFF)
        light_state = self.update_blink()
        if light_state:
            for (channel, speed) in enumerate(speeds):
                index = self.speed_to_index(speed)
                START_VAL = self.start_val(channel)
                for i in range(START_VAL,index+START_VAL):
                    self.pixels[self.hw.NEO_PIXEL_LIGHTS_ORDER[i]] = self.cfg.NEO_ERROR_COLOR
        self.pixels.show()

    def print_speed(self, speeds_and_directions):
        self.log_speed(speeds_and_directions)
        self.pixels.fill(self.OFF)
        for (channel, (speed, direction)) in enumerate (speeds_and_directions):
            # NeoFeather lights
            if direction == 1:
                direction_color = self.cfg.NEO_FORWARD_COLOR
            else:
                direction_color = self.cfg.NEO_REVERSE_COLOR
            index = self.speed_to_index(speed)
            START_VAL = self.start_val(channel)
            if index == 0:
                light_state = self.update_blink()
                if light_state:
                    self.pixels[self.hw.NEO_PIXEL_LIGHTS_ORDER[START_VAL]] = direction_color
            else:
                for i in range(START_VAL,index+START_VAL):
                    self.pixels[self.hw.NEO_PIXEL_LIGHTS_ORDER[i]] = direction_color
        self.pixels.show()

class OLEDDisplay(Display):
    def __init__(self, hw, cfg, logging):
        super().__init__(logging)
        self.hw = hw
        self.cfg = cfg
        self.speeds = [None] * hw.NUM_CHANNELS
        self.directions = [None] * hw.NUM_CHANNELS

        # Clear Display
        displayio.release_displays()

        # I2C Bus and Display Creation
        i2c = busio.I2C(hw.OLED_SCL_PIN, hw.OLED_SDA_PIN)
        self.display_bus = I2CDisplayBus(i2c, device_address=0x3C)
        self.display = adafruit_displayio_ssd1306.SSD1306(self.display_bus, width=hw.OLED_DISPLAY_WIDTH, height=hw.OLED_DISPLAY_HEIGHT)
        self.splash = displayio.Group()
        self.display.root_group = self.splash

        # Colors
        self.blank = displayio.Palette(1)
        self.blank[0] = 0x000000
        self.colored = displayio.Palette(1)
        self.colored[0] = 0xFFFFFF

    def set_borders(self):
        # Make borders
        outer_bitmap = displayio.Bitmap(self.hw.OLED_DISPLAY_WIDTH, self.hw.OLED_DISPLAY_HEIGHT, 1)
        outer_sprite = displayio.TileGrid(outer_bitmap, pixel_shader=self.colored, x=0, y=0)
        self.splash.append(outer_sprite)
        self.top_clear()
        self.bottom_clear()

    def top_clear(self):
        top_inner_bitmap = displayio.Bitmap(self.hw.OLED_DISPLAY_WIDTH - (self.cfg.OLED_BORDER_WIDTH * 2), self.cfg.OLED_TOP_HEIGHT - (self.cfg.OLED_BORDER_WIDTH * 2), 1)
        top_inner_sprite = displayio.TileGrid(top_inner_bitmap, pixel_shader=self.blank, x=1, y=1)
        self.splash.append(top_inner_sprite)

    def bottom_clear(self):
        bottom_inner_bitmap = displayio.Bitmap(self.hw.OLED_DISPLAY_WIDTH - (self.cfg.OLED_BORDER_WIDTH * 2), self.cfg.OLED_BOTTOM_HEIGHT - (self.cfg.OLED_BORDER_WIDTH * 2), 1)
        bottom_inner_sprite = displayio.TileGrid(bottom_inner_bitmap, pixel_shader=self.blank, x=1, y=(1 + self.cfg.OLED_TOP_HEIGHT))
        self.splash.append(bottom_inner_sprite)

    def show_direction(self):
        for (side, direction) in enumerate(self.directions):
            if self.directions[side] == 1:
                direction_text = "Forward"
            else:
                direction_text = "Reverse"
            direction_sprite = label.Label(terminalio.FONT, text=direction_text, color=self.colored[0], x=self.cfg.OLED_HORIZONTALS[side], y= self.cfg.OLED_VERTICALS[0] + self.cfg.OLED_TEXT_CENTERING_VALUE)
            self.splash.append(direction_sprite)

    def show_error(self):
        error_text = "Zero Speeds, Please"
        error_sprite = label.Label(terminalio.FONT, text=error_text, color=self.colored[0], x=self.cfg.OLED_HORIZONTALS[0], y= self.cfg.OLED_VERTICALS[0] + self.cfg.OLED_TEXT_CENTERING_VALUE)
        self.splash.append(error_sprite)

    def show_speed(self):
        for (side, speed) in enumerate(self.speeds):
            speed_text = f"{speed} %"
            speed_sprite = label.Label(terminalio.FONT, text=speed_text, color=self.colored[0], x=self.cfg.OLED_HORIZONTALS[side], y= self.cfg.OLED_VERTICALS[1] + self.cfg.OLED_TEXT_CENTERING_VALUE)

            bar_bitmap = displayio.Bitmap(round(self.cfg.OLED_BAR_WIDTH * speed/100), 8, 1)
            bar_sprite = displayio.TileGrid(bar_bitmap, pixel_shader=self.colored, x=self.cfg.OLED_HORIZONTALS[side], y=self.cfg.OLED_VERTICALS[2])

            self.splash.append(speed_sprite)
            self.splash.append(bar_sprite)

    def print_error(self, speeds, non_zeros):
        self.log_error(non_zeros)
        self.speeds = speeds
        self.bottom_clear()
        self.show_error()
        self.show_speed()

    def print_speed(self, speeds_and_directions):
        self.log_speed(speeds_and_directions)
        self.bottom_clear()
        for (side, (speed, direction)) in enumerate(speeds_and_directions):
            self.speeds[side] = speed
            self.directions[side] = direction
        self.show_speed()
        self.show_direction()

class DisplayConstructor:
    def __init__(self, hw, cfg, oled_display, neo_pixel_display, indicator_light):
        self.indicator = indicator_light
        self.NUM_DISPLAYS = len(hw.DISPLAY_TYPES)
        self.display = [None] * self.NUM_DISPLAYS
        i=0
        logging_state = True
        if "NEO_PIXEL" in hw.DISPLAY_TYPES:
            self.display[i] = neo_pixel_display(hw, cfg, logging=logging_state)
            i += 1
            logging_state = False
        if "OLED" in hw.DISPLAY_TYPES:
            self.display[i] = oled_display(hw, cfg, logging=logging_state)
            self.display[i].set_borders()
            i += 1
            logging_state = False

    def display_error(self, speeds, non_zeros):
        self.indicator.show_on()
        for i in range(self.NUM_DISPLAYS):
            self.display[i].print_error(speeds, non_zeros)

    def display_speed(self, speeds_and_directions):
        self.indicator.show_on()
        for i in range(self.NUM_DISPLAYS):
            self.display[i].print_speed(speeds_and_directions)

# This is here so I don't have to import all this into the main code just to do this there
display = DisplayConstructor(hw, cfg, OLEDDisplay, NEOPixelDisplay, indicator) 
