import os

# Path config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def get_asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)

# Common setup
PRIMARY_SCREEN_W = 1920
APP_WIDTH = 1280 
APP_HEIGHT = 720
FPS = 60
CAM_PREVIEW_SIZE = (320, 240)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
GOLD = (255, 215, 0)
GRAY_DARK = (40, 40, 40)
GRAY_LIGHT = (100, 100, 100)
BLUE_UI = (0, 120, 215)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GLASS_FILL = (30, 30, 35, 200)
GLASS_BORDER = (200, 200, 255, 60) 
NEON_GREEN = (57, 255, 20)        
NEON_BLUE = (0, 255, 255)
COLOR_MENU_BG = (15, 15, 20)

#Fonts
FONT_NAME_MAIN = "Arial"
FONT_SCALE_TITLE = 0.08
FONT_SIZE_UI_BASE = 22

# Game Rules
WIN_SCORE = 301
PICKUP_DURATION = 2.0 
THROW_COOLDOWN = 1.0
AIM_NOISE = 2
AI_CONFIDENCE_THRESHOLD = 0.85
SEQ_LEN = 60
HIP_TOLERANCE_Y = 0.15
HIP_TOLERANCE_X = 0.25

# Dartboard
R_BULLSEYE = 45
R_OUTER_BULL = 60
R_INNER_RING_START = 170
R_INNER_RING_END = 185
R_OUTER_RING_START = 280
R_OUTER_RING_END = 300
R_BOARD_EDGE = 380
SECTOR_VALUES = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]

#Game themes / Images
BOARD_SKINS = [
    get_asset_path("dartboard_1.png"),
    get_asset_path("dartboard_2.png")
]

BACKGROUND_SKINS = [
    get_asset_path("background_1.jpeg"),
    get_asset_path("background_2.jpeg")
]

HAND_IMG = get_asset_path("hand.png")