import board
if board.board_id == 'raspberry_pi_pico':
    import raspberry_pi_pico as hw
elif board.board_id == 'adafruit_feather_rp2040':
    import feather_rp2040 as hw

# Constants
OLED_TEXT_HEIGHT = 8
OLED_TEXT_CENTERING_VALUE = 4
OLED_TEXT_WIDTH_AND_SPACING = 5 + 1

# Usable by All
INT_HALF_CHANNELS = round(self.hw.NUM_CHANNELS / 2)

# UART Configuration
logging_state = True

# NEOPixel Configurations
NEO_FORWARD_COLOR = (0, 255, 0) # Green
NEO_REVERSE_COLOR = (255, 0, 0) # Red
NEO_ERROR_COLOR = (255,127,0) # Orange
NEO_SPEED_COLOR = NEO_ERROR_COLOR
NEO_DISPLAY_BRIGHTNESS = 0.025
NEO_SAME_SPEED_DIRECTION_BAR ‎ =  4
NEO_MODE_SELECT_BAR ‎ =  8
NEO_SAME_NUM_SPEED_PIXELS= (self.hw.NEO_PIXEL_NUM_LIGHTS - (NEO_SAME_SPEED_DIRECTION_BAR * INT_HALF_CHANNELS * 2))
NEO_SAME_SPEED_START_VAL = NEO_SAME_SPEED_DIRECTION_BAR * INT_HALF_CHANNELS
NEO_NO_MODE_LIGHTS = [1, 0, 0, 1, 0.5, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0, 0.5, 1, 0, 0, 1]       # 1 is on, 0.5 is blinking, 0 is off

# OLED Configuratoions
OLED_BORDER_WIDTH = 1
OLED_SPACING = 4
OLED_TOP_HEIGHT = int(hw.OLED_DISPLAY_HEIGHT / 4)       # Currently 16
OLED_BOTTOM_HEIGHT = int(hw.OLED_DISPLAY_HEIGHT * 3 / 4)      # Currently 48
OLED_NUM_VERTICALS = 3       # Current Verticals for direction text, speed text, and speed bar in that order
OLED_SPEED_BAR_HEIGHT = OLED_TEXT_HEIGHT
OLED_SELECT_UNDERLINE_HEIGHT = 2

OLED_SEPARATE_BAR_WIDTH = int(hw.OLED_DISPLAY_WIDTH / hw.NUM_CHANNELS) - (OLED_SPACING * 2)      # Currently 56
OLED_SAME_BAR_WIDTH = hw.OLED_DISPLAY_WIDTH - (OLED_SPACING * 2)      # Currently 120
OLED_HORIZONTALS = [None] * hw.NUM_CHANNELS
OLED_VERTICALS = [None] * OLED_NUM_VERTICALS
for channel in range(hw.NUM_CHANNELS):
    OLED_HORIZONTALS[channel] = OLED_SPACING + int(channel * hw.OLED_DISPLAY_WIDTH / hw.NUM_CHANNELS)       # Currently 4 and 68
for i in range(OLED_NUM_VERTICALS):
    OLED_VERTICALS[i] = OLED_TOP_HEIGHT + ((1 + (i * 2)) * OLED_SPACING) + (i * OLED_TEXT_HEIGHT)       # Currently 24, 40, and 52

# Modes
# Creation of functions with mode names to allow what I thought was simpler selection code
def separate_speed():
    pass
def same_speed():
    pass
def no_mode():
    pass
modes = [separate_speed, same_speed, no_mode, no_mode] # The code is currently set up for 4 modes
