import board
if board.board_id == 'raspberry_pi_pico':
    import raspberry_pi_pico as hw
elif board.board_id == 'adafruit_feather_rp2040':
    import feather_rp2040 as hw

# Constants
OLED_TEXT_HEIGHT = 8

# UART Configuration
logging_state = True

# NEOPixel Configurations
NEO_FORWARD_COLOR = (0, 255, 0) # Green
NEO_REVERSE_COLOR = (255, 0, 0) # Red
NEO_ERROR_COLOR = (255,127,0) # Orange
NEO_PIXEL_DISPLAY_BRIGHTNESS = 0.025

# OLED Configuratoions
OLED_BORDER_WIDTH = 1
OLED_SPACING = 4
OLED_TOP_HEIGHT = int(hw.OLED_DISPLAY_HEIGHT / 4)       # Currently 16
OLED_BOTTOM_HEIGHT = int(hw.OLED_DISPLAY_HEIGHT * 3 / 4)      # Currently 48
OLED_NUM_VERTICALS = 3       # Current Verticals for direction text, speed text, and speed bar in that order

OLED_BAR_WIDTH = int(hw.OLED_DISPLY_WIDTH / hw.NUM_CHANNELS) - (OLED_SPACING * 2)      # Currently 56
OLED_HORIZONTALS = [None] * hw.NUM_CHANNELS
OLED_VERTICALS = 
for channel in range(hw.NUM_CHANNELS):
    OLED_HORIZONTALS[channel] = OLED_SPACING + int(channel * hw.OLED_WIDTH / hw.NUM_CHANNELS)       # Currently 4 and 68
for i in range(OLED_NUM_VERTICALS):
    OLED_VERTICALS[i] = OLED_TOP_HEIGHT + ((1 + (i * 2)) * OLED_SPACING) + (i *OLED_TEXT_HEIGHT)       # Currently 24, 40, and 52
