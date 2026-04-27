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
font = pygame.font.SysFont(None, UI.TITLE_FONT_SIZE) # type: ignore
score_font = pygame.font.SysFont(None, UI.SCORE_FONT_SIZE) # type: ignore
countdown_font = pygame.font.SysFont(None, UI.COUNTDOWN_FONT_SIZE) # type: ignore
countdown_end_time = pygame.time.get_ticks() + UI.COUNTDOWN_SECONDS * 1000
player1_score = 0
player2_score = 0

# Spawn players at their kickoff positions.
player1 = Player(
    Players.PLAYER_1_ID,
    Players.PLAYER_1_START_X,
    Screen.HEIGHT // 2 - Players.START_Y_OFFSET,
    Players.HITBOX_WIDTH,
    Players.HITBOX_HEIGHT,
    Players.SPEED,
)
player2 = Player(
    Players.PLAYER_2_ID,
    Players.PLAYER_2_START_X,
    Screen.HEIGHT // 2 - Players.START_Y_OFFSET,
    Players.HITBOX_WIDTH,
    Players.HITBOX_HEIGHT,
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


def draw_score() -> None:
    """Draw the current score."""
    text = score_font.render(f"{player1_score} - {player2_score}", True, Colors.WHITE)
    SCREEN.blit(text, (Screen.WIDTH // 2 - text.get_width() // 2, UI.SCORE_Y))


def countdown_remaining() -> int:
    """Return whole seconds remaining in the post-goal countdown."""
    remaining_ms = max(0, countdown_end_time - pygame.time.get_ticks())
    return math.ceil(remaining_ms / 1000)


def draw_countdown() -> None:
    """Draw the active countdown number over the field."""
    remaining = countdown_remaining()
    if remaining <= 0:
        return

    text = countdown_font.render(str(remaining), True, Colors.WHITE)
    SCREEN.blit(
        text,
        (
            Screen.WIDTH // 2 - text.get_width() // 2,
            Screen.HEIGHT // 2 - text.get_height() // 2,
        ),
    )


def sync_player_state(player):
    """Write float position back to rect/sprite state after manual position edits."""
    player.rect.x = int(player.pos[0])
    player.rect.y = int(player.pos[1])
    player.update_sprite()


def clamp_player_to_field(player):
    """Keep a player inside the field after separation pushes."""
    min_x = Field.MARGIN
    max_x = Screen.WIDTH - Field.MARGIN - player.rect.width
    min_y = Field.MARGIN
    max_y = Screen.HEIGHT - Field.MARGIN - player.rect.height
    player.pos[0] = max(min_x, min(player.pos[0], max_x))
    player.pos[1] = max(min_y, min(player.pos[1], max_y))


def clamp_player_speed(player):
    """Cap post-collision speed so bounces feel small and controlled."""
    speed = math.hypot(player.velocity[0], player.velocity[1])
    max_allowed = player.max_speed * 1.05
    if speed > max_allowed and speed > 0:
        scale = max_allowed / speed
        player.velocity[0] *= scale
        player.velocity[1] *= scale


def resolve_player_player_collision(player_a, player_b):
    """Separate overlapping players and apply a small bounce impulse."""
    if not player_a.collides_with_player(player_b):
        return

    dx = player_a.rect.centerx - player_b.rect.centerx
    dy = player_a.rect.centery - player_b.rect.centery
    dist = math.hypot(dx, dy)

    if dist > 1e-6:
        nx = dx / dist
        ny = dy / dist
    else:
        rvx = player_a.velocity[0] - player_b.velocity[0]
        rvy = player_a.velocity[1] - player_b.velocity[1]
        rv_len = math.hypot(rvx, rvy)
        if rv_len > 1e-6:
            nx = rvx / rv_len
            ny = rvy / rv_len
        else:
            nx, ny = 1.0, 0.0

    # Tunables for player-player body feel.
    # `separation_step` controls how aggressively overlap is resolved.
    # `max_separation_iterations` prevents infinite loops in edge cases.
    separation_step = 0.8
    max_separation_iterations = 24
    for _ in range(max_separation_iterations):
        if not player_a.collides_with_player(player_b):
            break

        player_a.pos[0] += nx * separation_step
        player_a.pos[1] += ny * separation_step
        player_b.pos[0] -= nx * separation_step
        player_b.pos[1] -= ny * separation_step

        clamp_player_to_field(player_a)
        clamp_player_to_field(player_b)
        sync_player_state(player_a)
        sync_player_state(player_b)

    # Apply normal impulse only when players are moving into each other.
    # `restitution` controls bounceiness (0 = sticky, 1 = very bouncy).
    rvx = player_a.velocity[0] - player_b.velocity[0]
    rvy = player_a.velocity[1] - player_b.velocity[1]
    normal_speed = rvx * nx + rvy * ny
    restitution = 0.9
    if normal_speed < 0:
        impulse = -(1.0 + restitution) * normal_speed * 0.5
        player_a.velocity[0] += impulse * nx
        player_a.velocity[1] += impulse * ny
        player_b.velocity[0] -= impulse * nx
        player_b.velocity[1] -= impulse * ny

    # Small constant recoil gives visible feedback on gentle contacts.
    recoil = 0.12
    player_a.velocity[0] += recoil * nx
    player_a.velocity[1] += recoil * ny
    player_b.velocity[0] -= recoil * nx
    player_b.velocity[1] -= recoil * ny

    clamp_player_speed(player_a)
    clamp_player_speed(player_b)


def resolve_ball_player_collisions(players):
    """Resolve ball/player contacts with iterative impulses.

    Multiple passes handle squeeze cases where the ball touches both players
    in the same frame.
    """
    # Ball contact tuning:
    # `restitution` is bounceiness.
    # `tangential_transfer` transfers a bit of player side-motion into the ball.
    # `separation_slop` prevents tiny re-penetration jitter.
    restitution = 0.86
    tangential_transfer = 0.24
    separation_slop = 0.03
    max_solver_iterations = 6

    # Avoid injecting tangential energy multiple times per player per frame.
    tangential_applied_to = set()

    for _ in range(max_solver_iterations):
        had_collision = False

        for player in players:
            collision = player.get_ball_collision_normal(ball)
            if not collision:
                continue

            had_collision = True
            nx, ny, penetration = collision

            # Positional correction resolves overlap before velocity impulses.
            correction = max(0.0, penetration) + separation_slop
            ball.x += nx * correction
            ball.y += ny * correction

            # Reflect the ball in the moving player's frame, then convert back.
            pvx, pvy = player.velocity
            rvx = ball.vx - pvx
            rvy = ball.vy - pvy
            speed_into_surface = rvx * nx + rvy * ny

            if speed_into_surface < 0:
                impulse = -(1.0 + restitution) * speed_into_surface
                rvx += impulse * nx
                rvy += impulse * ny

            # Tangential transfer adds "spin-like" influence on glancing hits.
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
    """Advance ball with sub-steps to prevent frame-skipping through colliders."""
    speed = math.hypot(ball.vx, ball.vy)
    # Smaller step size = more robust collisions at high speed.
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
    global player1_score, player2_score

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

        countdown_active = countdown_remaining() > 0
        if not countdown_active:
            player1.handle_input(player2)
            player2.handle_input(player1)
            resolve_player_player_collision(player1, player2)

            advance_ball([player1, player2])

            # Check for goals
            if ball.x - ball.radius < Field.MARGIN + Field.GOAL_WIDTH and left_goal.top < ball.y < left_goal.bottom:
                player2_score += 1
                print("Goal for Player 2!")
                reset(start_countdown=True)
            elif ball.x + ball.radius > Screen.WIDTH - Field.MARGIN - Field.GOAL_WIDTH and right_goal.top < ball.y < right_goal.bottom:
                player1_score += 1
                print("Goal for Player 1!")
                reset(start_countdown=True)

        draw_field()

        # Draw players
        player1.draw(SCREEN)
        player2.draw(SCREEN)
        draw_score()
        draw_countdown()

        pygame.display.flip()

def reset(start_countdown: bool = False):
    global player1, player2, countdown_end_time
    ball.x = BallConfig.START_X
    ball.y = BallConfig.START_Y
    ball.vx = 0
    ball.vy = 0

    player1 = Player(
        Players.PLAYER_1_ID,
        Players.PLAYER_1_START_X,
        Screen.HEIGHT // 2 - Players.START_Y_OFFSET,
        Players.HITBOX_WIDTH,
        Players.HITBOX_HEIGHT,
        Players.SPEED,
    )

    player2 = Player(
        Players.PLAYER_2_ID,
        Players.PLAYER_2_START_X,
        Screen.HEIGHT // 2 - Players.START_Y_OFFSET,
        Players.HITBOX_WIDTH,
        Players.HITBOX_HEIGHT,
        Players.SPEED,
    )

    if start_countdown:
        countdown_end_time = pygame.time.get_ticks() + UI.COUNTDOWN_SECONDS * 1000
    else:
        countdown_end_time = 0

if __name__ == "__main__":
    run_game()
