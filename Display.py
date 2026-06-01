import board
import displayio
import terminalio
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus
import busio
import neopixel
import adafruit_displayio_ssd1306
import digitalio
if board.board_id == 'raspberry_pi_pico':
    import raspberry_pi_pico as hw
elif board.board_id == 'adafruit_feather_rp2040':
    import feather_rp2040 as hw

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
            self.PURPLE = (120, 0, 120)
            self.OFF = (0,0,0)
        elif board.board_id == 'adafruit_feather_rp2040':
            self.indicator_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=100)

    def update(self):
        self.cycle_count = (self.cycle_count + 1) % self.CYCLES_PER_TOGGLE
        if self.cycle_count == 0:
            if self.light_state:
                self.light_state = 0
                if board.board_id == 'adafruit_feather_rp2040':
                    self.indicator_pixel[0] = self.OFF
                elif board.board_id == 'raspberry_pi_pico':
                    self.indicator_pixel = self.light_state
            else:
                self.light_state = 1
                if board.board_id == 'adafruit_feather_rp2040':
                    self.indicator_pixel[0] = self.PURPLE
                elif board.board_id == 'raspberry_pi_pico':
                    self.indicator_pixel = self.light_state
        return self.light_state

class OLEDDisplay:
    def __init__(self, hw):
        self.hw = hw
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
        top_inner_bitmap = displayio.Bitmap(self.hw.OLED_DISPLAY_WIDTH-2, int(self.hw.OLED_DISPLAY_HEIGHT/4)-2, 1)
        top_inner_sprite = displayio.TileGrid(top_inner_bitmap, pixel_shader=self.blank, x=1, y=1)
        self.splash.append(top_inner_sprite)

    def bottom_clear(self):
        bottom_inner_bitmap = displayio.Bitmap(self.hw.OLED_DISPLAY_WIDTH-2, int(self.hw.OLED_DISPLAY_HEIGHT*3/4)-2, 1)
        bottom_inner_sprite = displayio.TileGrid(bottom_inner_bitmap, pixel_shader=self.blank, x=1, y=1+int(self.hw.OLED_DISPLAY_HEIGHT/4))
        self.splash.append(bottom_inner_sprite)

    def print_speed(self, speeds_and_directions, light_state):
        self.bottom_clear()
        for (side, (speed, direction)) in enumerate(speeds_and_directions):
                self.speeds[side] = speed
                self.directions[side] = direction
        self.show_speed()
        self.show_direction()

    def print_error(self, speeds, light_state, non_zeros):
        self.speeds = speeds
        self.bottom_clear()
        self.show_error()
        self.show_speed()

    def show_direction(self):
        for (side, direction) in enumerate(self.directions):
            if self.directions[side] == 1:
                direction_text = "Forward"
            else:
                direction_text = "Reverse"
            direction_sprite = label.Label(terminalio.FONT, text=direction_text, color=self.colored[0], x=self.hw.OLED_HORIZONTALS[side], y=self.hw.OLED_VERTICALS[0])
            self.splash.append(direction_sprite)

    def show_error(self):
        error_text = "Zero Speeds, Please"
        error_sprite = label.Label(terminalio.FONT, text=error_text, color=self.colored[0], x=self.hw.OLED_HORIZONTALS[0], y=self.hw.OLED_VERTICALS[0])
        self.splash.append(error_sprite)

    def show_speed(self):
        for (side, speed) in enumerate(self.speeds):
            speed_text = f"{speed} %"
            speed_sprite = label.Label(terminalio.FONT, text=speed_text, color=self.colored[0], x=self.hw.OLED_HORIZONTALS[side], y=self.hw.OLED_VERTICALS[1])

            bar_bitmap = displayio.Bitmap(round(self.hw.OLED_BAR_WIDTH * speed/100), 8, 1)
            bar_sprite = displayio.TileGrid(bar_bitmap, pixel_shader=self.colored, x=self.hw.OLED_HORIZONTALS[side], y=self.hw.OLED_VERTICALS[2])

            self.splash.append(speed_sprite)
            self.splash.append(bar_sprite)

class NEOPixelDisplay:
    def __init__(self, hw):
        # Colors
        self.hw = hw
        self.OFF = (0, 0, 0)
        self.FORWARD_COLOR = (0, 255, 0)
        self.REVERSE_COLOR = (255, 0, 0)
        self.ERROR_COLOR = (255,127,0)

        # Display init
        self.pixels = neopixel.NeoPixel(hw.NEOPIXEL_PIN, hw.NUM_LIGHTS, brightness=hw.NEO_PIXEL_DISPLAY_BRIGHTNESS)
        self.pixels.auto_write = False
        self.pixels.fill(self.OFF)

    def speed_to_index(self, speed):
        """
        Convert the speed percentage into pixel index
        """
        return speed * self.hw.NUM_LIGHTS / self.hw.NUM_CHANNELS

    def print_error(self, speeds, light_state, non_zeros):
        self.pixels.fill(self.OFF)
        if light_state:
            for (channel, speed) in enumerate(speeds):
                index = self.speed_to_index(speed)
                START_VAL = int(channel * (self.hw.NUM_LIGHTS / self.hw.NUM_CHANNELS))
                for i in range(START_VAL,index+START_VAL):
                    self.pixels[self.hw.NEO_PIXEL_LIGHTS_ORDER[i]] = self.ERROR_COLOR
        self.pixels.show()

    def print_speed(self, speeds_and_directions, lights_state):
        self.pixels.fill(self.OFF)
        for (channel, (speed, direction)) in enumerate (speeds_and_directions):
            # NeoFeather lights
            if direction == 1:
                direction_color = self.FORWARD_COLOR
            else:
                direction_color = self.REVERSE_COLOR
            index = self.speed_to_index(speed)
            START_VAL = int(channel * (self.hw.NUM_LIGHTS / self.hw.NUM_CHANNELS))
            if index == 0:
                if lights_state:
                    self.pixels[self.hw.NEO_PIXEL_LIGHTS_ORDER[START_VAL]] = direction_color
            else:
                for i in range(START_VAL,index+START_VAL):
                    self.pixels[self.hw.NEO_PIXEL_LIGHTS_ORDER[i]] = direction_color
        self.pixels.show()

class UARTDisplay:
    # def __init__(self):
        # I don't know what, if anything, to put here

    def print_error(self, speeds, light_state, non_zeros):
        print("Set Servo(s)", non_zeros, "to zero to start.")

    def print_speed(self, speeds_and_directions, light_state):
        for (channel, (speed, direction)) in enumerate(speeds_and_directions):
            print(f"Servo {channel}: {speed * direction}")

class SingleDisplay:
    # Needs testing and debugging
    def __init__(self, PixelBlinking, OLEDDisplay, NEOPixelDisplay, UARTDisplay, hw):
        self.lights_blink = PixelBlinking()
        if "OLED" in hw.DISPLAY_TYPES:
            self.display = OLEDDisplay(hw)
        if "NEO_PIXEL" in hw.DISPLAY_TYPES:
            self.display = NEOPixelDisplay(hw)
        if "UART" in hw.DISPLAY_TYPES:
            self.display = UARTDisplay()

    def display_error(self, speeds, non_zeros):
        light_state = self.lights_blink.update()
        self.display.print_error(speeds, light_state, non_zeros)

    def display_speed(self, speeds_and_directions):
        light_state = self.lights_blink.update()
        self.display.print_speed(speeds_and_directions, light_state)

class MultiDisplay:
    def __init__(self, PixelBlinking, OLEDDisplay, NEOPixelDisplay, UARTDisplay, hw):
        self.lights_blink = PixelBlinking()
        self.NUM_DISPLAYS = len(hw.DISPLAY_TYPES)
        i=0
        self.display = [None] * self.NUM_DISPLAYS
        if "OLED" in hw.DISPLAY_TYPES:
            self.display[i] = OLEDDisplay(hw)
            i += 1
        if "NEO_PIXEL" in hw.DISPLAY_TYPES:
            self.display[i] = NEOPixelDisplay(hw)
            i += 1
        if "UART" in hw.DISPLAY_TYPES:
            self.display[i] = UARTDisplay()
            i += 1

    def display_error(self, speeds, non_zeros):
        light_state = self.lights_blink.update()
        for i in range(self.NUM_DISPLAYS):
            self.display[i].print_error(speeds, light_state, non_zeros)

    def display_speed(self, speeds_and_directions):
        light_state = self.lights_blink.update()
        for i in range(self.NUM_DISPLAYS):
            self.display[i].print_speed(speeds_and_directions, light_state)
