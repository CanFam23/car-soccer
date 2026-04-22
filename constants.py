"""Game constants.

Add new constants by adding to the class that best fits.
"""

import math

import pygame


class Screen:
    WIDTH = 1000
    HEIGHT = 600
    SIZE = (WIDTH, HEIGHT)
    TITLE = "Rocket League"
    FPS = 60


class Colors:
    BLACK = (10, 10, 10)
    WHITE = (240, 240, 240)
    GREEN = (40, 120, 40)
    BLUE = (80, 170, 255)
    RED = (255, 90, 90)
    YELLOW = (255, 220, 80)


class Field:
    MARGIN = 40
    GOAL_WIDTH = 14
    GOAL_HEIGHT = 150
    CENTER_CIRCLE_RADIUS = 70
    LINE_WIDTH = 4


class Ball:
    RADIUS = 12
    START_X = Screen.WIDTH // 2
    START_Y = Screen.HEIGHT // 2


class UI:
    TITLE_TEXT = Screen.TITLE
    TITLE_FONT_SIZE = 40
    TITLE_Y = 10


class App:
    QUIT_KEY = pygame.K_q


class Players:
    PLAYER_1_ID = 1
    PLAYER_2_ID = 2

    PLAYER_1_START_X = 800
    PLAYER_2_START_X = 80
    START_Y_OFFSET = 20

    WIDTH = 40
    HEIGHT = 40
    SPEED = 7

    INITIAL_DIRECTION = (1, 0)
    # Preserves the existing rotation behavior in player.py.
    ROTATION_STEP = math.radians(360)
    COLOR = Colors.RED

    NORMALS = {
        'back':(0,1),
        'front':(0,-1),
        'right':(-1,0),
        'left':(1,0)
    }

class Controls:
    PLAYER = {
        Players.PLAYER_1_ID: {
            "rotate_right": pygame.K_LEFT,
            "rotate_left": pygame.K_RIGHT,
            "move_forward": pygame.K_UP,
            "move_back": pygame.K_DOWN,
        },
        Players.PLAYER_2_ID: {
            "rotate_right": pygame.K_a,
            "rotate_left": pygame.K_d,
            "move_forward": pygame.K_w,
            "move_back": pygame.K_s,
        },
    }
