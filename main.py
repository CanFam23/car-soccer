import sys
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

        ball.update()

        # Check for goals
        if ball.x - ball.radius < Field.MARGIN + Field.GOAL_WIDTH and left_goal.top < ball.y < left_goal.bottom:
            print("Goal for Player 2!")
            reset()
        elif ball.x + ball.radius > Screen.WIDTH - Field.MARGIN - Field.GOAL_WIDTH and right_goal.top < ball.y < right_goal.bottom:
            print("Goal for Player 1!")
            reset()

        # Check collisions with players
        for player in [player1, player2]:
            collision = player.get_ball_collision_normal(ball)
            if not collision:
                continue

            nx, ny, penetration = collision

            # Positional correction prevents repeated "stuck" collisions.
            ball.x += nx * (penetration + 0.01)
            ball.y += ny * (penetration + 0.01)

            # Work in the player moving frame so player motion transfers naturally.
            pvx, pvy = player.velocity
            rvx = ball.vx - pvx
            rvy = ball.vy - pvy
            speed_into_surface = rvx * nx + rvy * ny

            restitution = 0.86

            if speed_into_surface < 0:
                impulse = -(1.0 + restitution) * speed_into_surface
                rvx += impulse * nx
                rvy += impulse * ny

            # Add some side spin/drag from player's tangential movement.
            tx, ty = -ny, nx
            tangential_player_speed = pvx * tx + pvy * ty
            tangential_transfer = 0.24
            rvx += tangential_transfer * tangential_player_speed * tx
            rvy += tangential_transfer * tangential_player_speed * ty

            ball.vx = rvx + pvx
            ball.vy = rvy + pvy

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
