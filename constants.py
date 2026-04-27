"""Game constants.

Add new constants by adding to the class that best fits.
"""

import math
from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parent


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
    SPRITE = BASE_DIR / "sprites" / "ball" / "football.png"


class UI:
    TITLE_TEXT = Screen.TITLE
    TITLE_FONT_SIZE = 40
    TITLE_Y = 10
    SCORE_FONT_SIZE = 42
    SCORE_Y = 48
    COUNTDOWN_FONT_SIZE = 96
    COUNTDOWN_SECONDS = 3


class App:
    QUIT_KEY = pygame.K_q


class Players:
    PLAYER_1_ID = 1
    PLAYER_2_ID = 2

    VISUAL_WIDTH = 64
    VISUAL_HEIGHT = 64
    HITBOX_WIDTH = 46
    HITBOX_HEIGHT = 46

    PLAYER_1_START_X = Screen.WIDTH - (VISUAL_WIDTH * 2)
    PLAYER_2_START_X = 80
    START_Y_OFFSET = 20

    SPEED = 7
    SPRITES = {
        PLAYER_1_ID: BASE_DIR / "sprites" / "cars" / "RedStrip.png",
        PLAYER_2_ID: BASE_DIR / "sprites" / "cars" / "WhiteStrip.png",
    }

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
