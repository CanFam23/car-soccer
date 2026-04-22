import sys
import math
import pygame

from ball import Ball
from constants import App, Ball as BallConfig, Colors, Field, Players, Screen, UI
from player import Player

pygame.init()

SCREEN = pygame.display.set_mode(Screen.SIZE)
pygame.display.set_caption(Screen.TITLE)
CLOCK = pygame.time.Clock()

left_goal = pygame.Rect(
    Field.MARGIN,
    Screen.HEIGHT // 2 - Field.GOAL_HEIGHT // 2,
    Field.GOAL_WIDTH,
    Field.GOAL_HEIGHT,
)
right_goal = pygame.Rect(
    Screen.WIDTH - Field.MARGIN - Field.GOAL_WIDTH,
    Screen.HEIGHT // 2 - Field.GOAL_HEIGHT // 2,
    Field.GOAL_WIDTH,
    Field.GOAL_HEIGHT,
)

ball = Ball(BallConfig.START_X, BallConfig.START_Y, BallConfig.RADIUS, Colors.YELLOW)
font = pygame.font.SysFont(None, UI.TITLE_FONT_SIZE)

# starting x, y, width, height, and speed
player1 = Player(
    Players.PLAYER_1_ID,
    Players.PLAYER_1_START_X,
    Screen.HEIGHT // 2 - Players.START_Y_OFFSET,
    Players.WIDTH,
    Players.HEIGHT,
    Players.SPEED,
)
player2 = Player(
    Players.PLAYER_2_ID,
    Players.PLAYER_2_START_X,
    Screen.HEIGHT // 2 - Players.START_Y_OFFSET,
    Players.WIDTH,
    Players.HEIGHT,
    Players.SPEED,
)


def draw_field():
    """Draw the field, goals, ball, and heading."""
    SCREEN.fill(Colors.BLACK)

    # Background
    pygame.draw.rect(
        SCREEN,
        Colors.GREEN,
        (
            Field.MARGIN,
            Field.MARGIN,
            Screen.WIDTH - 2 * Field.MARGIN,
            Screen.HEIGHT - 2 * Field.MARGIN,
        ),
    )

    # Middle line
    pygame.draw.line(
        SCREEN,
        Colors.WHITE,
        (Screen.WIDTH // 2, Field.MARGIN),
        (Screen.WIDTH // 2, Screen.HEIGHT - Field.MARGIN),
        Field.LINE_WIDTH,
    )

    # Middle circle
    pygame.draw.circle(
        SCREEN,
        Colors.WHITE,
        (Screen.WIDTH // 2, Screen.HEIGHT // 2),
        Field.CENTER_CIRCLE_RADIUS,
        Field.LINE_WIDTH,
    )

    # Draw goals
    pygame.draw.rect(SCREEN, Colors.BLUE, left_goal)
    pygame.draw.rect(SCREEN, Colors.RED, right_goal)

    # Draw ball
    ball.draw(SCREEN)

    text = font.render(UI.TITLE_TEXT, True, Colors.WHITE)
    SCREEN.blit(text, (Screen.WIDTH // 2 - text.get_width() // 2, UI.TITLE_Y))


def resolve_ball_player_collisions(players):
    """Resolve ball-vs-player contacts with iterative solving.

    Multiple passes are important when the ball is squeezed by both players
    in the same frame.
    """
    restitution = 0.86
    tangential_transfer = 0.24
    separation_slop = 0.03
    max_solver_iterations = 6

    # Avoid adding tangential energy multiple times from the same player
    # during iterative resolution in one frame.
    tangential_applied_to = set()

    for _ in range(max_solver_iterations):
        had_collision = False

        for player in players:
            collision = player.get_ball_collision_normal(ball)
            if not collision:
                continue

            had_collision = True
            nx, ny, penetration = collision

            # Positional correction keeps the ball from tunneling through
            # when multiple bodies are interacting in one frame.
            correction = max(0.0, penetration) + separation_slop
            ball.x += nx * correction
            ball.y += ny * correction

            # Work in player-relative frame.
            pvx, pvy = player.velocity
            rvx = ball.vx - pvx
            rvy = ball.vy - pvy
            speed_into_surface = rvx * nx + rvy * ny

            if speed_into_surface < 0:
                impulse = -(1.0 + restitution) * speed_into_surface
                rvx += impulse * nx
                rvy += impulse * ny

            # Tangential transfer gives glancing hits better feel.
            if player.id not in tangential_applied_to:
                tx, ty = -ny, nx
                tangential_player_speed = pvx * tx + pvy * ty
                rvx += tangential_transfer * tangential_player_speed * tx
                rvy += tangential_transfer * tangential_player_speed * ty
                tangential_applied_to.add(player.id)

            ball.vx = rvx + pvx
            ball.vy = rvy + pvy

        if not had_collision:
            break


def resolve_ball_wall_bounce():
    """Bounce the ball off field boundaries."""
    if ball.x - ball.radius < Field.MARGIN:
        ball.x = Field.MARGIN + ball.radius
        ball.vx = -ball.vx
    elif ball.x + ball.radius > Screen.WIDTH - Field.MARGIN:
        ball.x = Screen.WIDTH - Field.MARGIN - ball.radius
        ball.vx = -ball.vx

    if ball.y - ball.radius < Field.MARGIN:
        ball.y = Field.MARGIN + ball.radius
        ball.vy = -ball.vy
    elif ball.y + ball.radius > Screen.HEIGHT - Field.MARGIN:
        ball.y = Screen.HEIGHT - Field.MARGIN - ball.radius
        ball.vy = -ball.vy


def advance_ball(players):
    """Advance the ball with sub-steps so it cannot tunnel through players."""
    speed = math.hypot(ball.vx, ball.vy)
    max_step_distance = max(1.0, ball.radius * 0.25)
    steps = max(1, int(math.ceil(speed / max_step_distance)))

    for _ in range(steps):
        ball.x += ball.vx / steps
        ball.y += ball.vy / steps
        resolve_ball_wall_bounce()
        resolve_ball_player_collisions(players)

    # Apply frame friction once after all sub-steps.
    ball.vx *= ball.friction
    ball.vy *= ball.friction
    if abs(ball.vx) < 0.1:
        ball.vx = 0
    if abs(ball.vy) < 0.1:
        ball.vy = 0


def run_game():
    while True:
        CLOCK.tick(Screen.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[App.QUIT_KEY]:
            pygame.quit()
            sys.exit()

        player1.handle_input(player2)
        player2.handle_input(player1)

        advance_ball([player1, player2])

        # Check for goals
        if ball.x - ball.radius < Field.MARGIN + Field.GOAL_WIDTH and left_goal.top < ball.y < left_goal.bottom:
            print("Goal for Player 2!")
            reset()
        elif ball.x + ball.radius > Screen.WIDTH - Field.MARGIN - Field.GOAL_WIDTH and right_goal.top < ball.y < right_goal.bottom:
            print("Goal for Player 1!")
            reset()

        draw_field()

        # Draw players
        player1.draw(SCREEN)
        player2.draw(SCREEN)

        pygame.display.flip()

def reset():
    global player1, player2
    ball.x = BallConfig.START_X
    ball.y = BallConfig.START_Y
    ball.vx = 0
    ball.vy = 0

    player1 = Player(
        Players.PLAYER_1_ID,
        Players.PLAYER_1_START_X,
        Screen.HEIGHT // 2 - Players.START_Y_OFFSET,
        Players.WIDTH,
        Players.HEIGHT,
        Players.SPEED,
    )
    player2 = Player(
        Players.PLAYER_2_ID,
        Players.PLAYER_2_START_X,
        Screen.HEIGHT // 2 - Players.START_Y_OFFSET,
        Players.WIDTH,
        Players.HEIGHT,
        Players.SPEED,
    )


if __name__ == "__main__":
    run_game()
