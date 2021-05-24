# You can uncomment any lines to try some futures

# # # Screen size # # #
WIDTH, HEIGHT = 1280, 720  # HD
# WIDTH, HEIGHT = 1120, 640  # faster
# WIDTH, HEIGHT = 1920, 1080  # FullHD, too slow

# # # Graphics # # #
DRAW_SHADOWS = 1
# DRAW_SHADOWS = 0

SHADOWS_SHIFT = 11, 11
# Red, Green, Blue, Alpha
SHADOWS_COLOR = 110, 110, 110, 255
PLAYER_CAR_SHADOW_COLOR = 120, 110, 110, 255
# You may make your car`s shadow colorful
# PLAYER_CAR_SHADOW_COLOR = 0, 150, 150, 255
# PLAYER_CAR_SHADOW_COLOR = 200, 50, 50, 255

SECONDARY_SHADOWS_COLOR = 110, 110, 110, 0

# See others in PIL.ImageFilter
SHADOWS_FILTER = 'GaussianBlur(2.5)'  # Normal
# SHADOWS_FILTER = 'GaussianBlur(0)'  # No filter
# SHADOWS_FILTER = 'GaussianBlur(10)'  # Too smooth
# SHADOWS_FILTER = 'BLUR'
# SHADOWS_FILTER = 'BoxBlur(5)'
# SHADOWS_FILTER = 'FIND_EDGES'  # For fun
# SHADOWS_FILTER = 'CONTOUR'  # For fun

# Player car control
MAX_FORWARD_SPEED = 25
MAX_BACKWARD_SPEED = -12
MAX_DRIVE_FORCE = 30
MAX_LATERAL_IMPULSE = 0.45
ANGULAR_FRICTION_IMPULSE = 0.3
LINEAR_FRICTION_IMPULSE = 0.2

# Frames per second
FPS = 70
# FPS = 65
# FPS = 55  # minimum
# FPS = 80
# FPS = 100  # For NASA computers only :)

# # # Sounds # # #
PLAY_SOUNDS = 1

# # # Pixels per box2d meter [don`t change this] # # #
PPM = 32
