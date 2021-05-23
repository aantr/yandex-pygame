# You can uncomment any lines to try some futures

# # # Screen size # # #
WIDTH, HEIGHT = 1280, 720
# WIDTH, HEIGHT = 1120, 640

# # # Graphics # # #
DRAW_SHADOWS = 1
# DRAW_SHADOWS = 0

# Red, Green, Blue, Alpha
SHADOWS_COLOR = 110, 110, 110, 255
PLAYER_CAR_SHADOW_COLOR = 120, 110, 110, 255
# You may make your car`s shadow colorful
# PLAYER_CAR_SHADOW_COLOR = 0, 110, 110, 255
# PLAYER_CAR_SHADOW_COLOR = 200, 50, 50, 255

SECONDARY_SHADOWS_COLOR = 0, 0, 0, 0

# See others in PIL.ImageFilter
SHADOWS_FILTER = 'GaussianBlur(5)'
# SHADOWS_FILTER = 'GaussianBlur(10)'
# SHADOWS_FILTER = 'BLUR'
# SHADOWS_FILTER = 'BoxBlur(5)'
# SHADOWS_FILTER = 'FIND_EDGES'  # For fun
# SHADOWS_FILTER = 'CONTOUR'  # For fun

# Frames per second
FPS = 70
# FPS = 55  # minimum
# FPS = 85  # For PRO
# FPS = 100  # For NASA computers only :)

# # # Sounds # # #
PLAY_SOUNDS = 1

# # # Pixels per box2d meter [don`t change this] # # #
PPM = 32
