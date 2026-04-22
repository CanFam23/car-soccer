from __future__ import annotations

import pygame
import math

from ball import Ball
from constants import Controls, Players, Field, Screen


class Player:
    def __init__(self, id: int, x: int, y: int, width: int, height: int, speed: int) -> None:
        """Creates a new player with car-like movement."""
        self.id = id

        # float position for smoother movement
        self.pos = [float(x), float(y)]
        self.width = width
        self.height = height

        # logical center-based rect used for general placement
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # facing direction
        if self.id == Players.PLAYER_1_ID:
            self.direction = [-1.0, 0.0]  # face left
            self.side_order = ['back', 'front', 'right', 'left']
        else:
            self.direction = [1.0, 0.0]   # face right
            self.side_order = ['front', 'back', 'left', 'right']

        # movement state
        self.move_dir = 0   # 1 forward, -1 backward, 0 idle

        # car-like motion
        # Velocity vector [vx, vy]
        self.velocity = [0.0, 0.0]
        self.accel = 0.2
        self.max_speed = float(speed)
        self.max_reverse_speed = float(speed) * 0.6
        self.friction = 0.96

        # turning
        self.theta = Players.ROTATION_STEP

        # base sprite used for rotation
        self.base_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.base_image.fill(Players.COLOR)

        # rotated draw/collision state
        self.image = self.base_image
        self.mask = pygame.mask.from_surface(self.image)

        # bounding rect of rotated image
        self.rotated_rect = self.image.get_rect(center=self.rect.center)

        self.update_sprite()

    def update_sprite(self) -> None:
        """Update rotated image, mask, and rotated bounding rect."""
        angle = math.degrees(math.atan2(self.direction[1], self.direction[0]))
        self.image = pygame.transform.rotate(self.base_image, -angle)
        self.rotated_rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def rotate(self, angle: float) -> None:
        """Rotate the facing direction by angle degrees."""
        angle_rad = math.radians(angle)

        cos_theta = math.cos(angle_rad)
        sin_theta = math.sin(angle_rad)

        dx, dy = self.direction
        new_x = dx * cos_theta - dy * sin_theta
        new_y = dx * sin_theta + dy * cos_theta

        length = math.sqrt(new_x ** 2 + new_y ** 2)
        if length != 0:
            new_x /= length
            new_y /= length

        self.direction = [new_x, new_y]
        self.update_sprite()

    def collides_with_player(self, other: "Player") -> bool:
        """Pixel-perfect rotated collision against another player."""
        if not self.rotated_rect.colliderect(other.rotated_rect):
            return False

        offset = (
            other.rotated_rect.left - self.rotated_rect.left,
            other.rotated_rect.top - self.rotated_rect.top
        )
        return self.mask.overlap(other.mask, offset) is not None

    def get_collision_side_player(self, other: "Player"):
        """
        Approximate side using centers.
        With rotated collisions there is no true rect side anymore,
        so this uses the direction from other -> self.
        """
        if not self.collides_with_player(other):
            return None

        dx = self.rect.centerx - other.rect.centerx
        dy = self.rect.centery - other.rect.centery

        dist = math.hypot(dx, dy)
        if dist == 0:
            return "unknown"

        nx = dx / dist
        ny = dy / dist

        if abs(nx) > abs(ny):
            return "right" if nx > 0 else "left"
        else:
            return "bottom" if ny > 0 else "top"

    def get_collision_side_ball(self, other: Ball):
        cx, cy = other.x, other.y

        closest_x = max(self.rect.left, min(cx, self.rect.right))
        closest_y = max(self.rect.top,  min(cy, self.rect.bottom))

        dx = cx - closest_x
        dy = cy - closest_y

        distance = math.hypot(dx, dy)

        # no collision
        if distance > other.radius:
            return None

        # fallback if exactly overlapping
        if distance == 0:
            dx = cx - self.rect.centerx
            dy = cy - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance == 0:
                return "unknown"

        nx = dx / distance
        ny = dy / distance

        if abs(nx) > abs(ny):
            return self.side_order[0] if nx > 0 else self.side_order[1]
        else:
            return self.side_order[2] if ny > 0 else self.side_order[3]

    def get_ball_collision_normal(self, ball: Ball):
        """Return collision normal/penetration for a ball against the rotated player body.

        The normal points from the player toward the ball.
        Returns ``(nx, ny, penetration)`` or ``None`` when not colliding.
        """
        # Player orientation basis
        fx, fy = self.direction
        forward_len = math.hypot(fx, fy)
        if forward_len == 0:
            fx, fy = 1.0, 0.0
        else:
            fx /= forward_len
            fy /= forward_len
        rx, ry = -fy, fx

        cx, cy = self.rect.centerx, self.rect.centery
        bx, by = float(ball.x), float(ball.y)

        # Ball center in player-local coordinates.
        rel_x = bx - cx
        rel_y = by - cy
        local_x = rel_x * rx + rel_y * ry
        local_y = rel_x * fx + rel_y * fy

        half_w = self.width * 0.5
        half_h = self.height * 0.5

        # Closest point on the oriented rectangle in local coords.
        clamped_x = max(-half_w, min(local_x, half_w))
        clamped_y = max(-half_h, min(local_y, half_h))
        closest_x = cx + rx * clamped_x + fx * clamped_y
        closest_y = cy + ry * clamped_x + fy * clamped_y

        dx = bx - closest_x
        dy = by - closest_y
        dist = math.hypot(dx, dy)

        # No collision.
        if dist >= ball.radius:
            return None

        # Standard circle-vs-OBB contact.
        if dist > 1e-6:
            nx = dx / dist
            ny = dy / dist
            penetration = ball.radius - dist
            return nx, ny, penetration

        # Ball center is on/in the body: pick nearest face normal in local frame.
        dist_to_x_face = half_w - abs(local_x)
        dist_to_y_face = half_h - abs(local_y)

        if dist_to_x_face < dist_to_y_face:
            sign = 1.0 if local_x >= 0 else -1.0
            nx = rx * sign
            ny = ry * sign
            penetration = ball.radius + dist_to_x_face
        else:
            sign = 1.0 if local_y >= 0 else -1.0
            nx = fx * sign
            ny = fy * sign
            penetration = ball.radius + dist_to_y_face

        normal_len = math.hypot(nx, ny)
        if normal_len == 0:
            return None
        nx /= normal_len
        ny /= normal_len
        return nx, ny, penetration

    def handle_input(self, other: "Player") -> None:
        keys = pygame.key.get_pressed()
        controls = Controls.PLAYER.get(self.id)
        if not controls:
            return

        # Signed speed along the current facing direction.
        speed_along_direction = (
            self.velocity[0] * self.direction[0] +
            self.velocity[1] * self.direction[1]
        )

        if speed_along_direction == 0:
            self.move_dir = 0

        if keys[controls["move_forward"]]:
            speed_along_direction += self.accel
            self.move_dir = 1

        if keys[controls["move_back"]]:
            speed_along_direction -= self.accel
            self.move_dir = -1

        if speed_along_direction > self.max_speed:
            speed_along_direction = self.max_speed
        if speed_along_direction < -self.max_reverse_speed:
            speed_along_direction = -self.max_reverse_speed

        if abs(speed_along_direction) > 0.03:
            turn_amount = self.theta
            if speed_along_direction < 0:
                turn_amount *= -1

            if keys[controls["rotate_right"]]:
                self.rotate(-turn_amount)

            if keys[controls["rotate_left"]]:
                self.rotate(turn_amount)

        speed_along_direction *= self.friction

        if abs(speed_along_direction) < 0.02:
            speed_along_direction = 0.0

        # Keep vector velocity aligned to the facing direction.
        self.velocity[0] = self.direction[0] * speed_along_direction
        self.velocity[1] = self.direction[1] * speed_along_direction

        old_pos = self.pos[:]
        old_center = self.rect.center

        new_x = self.pos[0] + self.velocity[0]
        new_y = self.pos[1] + self.velocity[1]

        # boundary checks using the unrotated logical body
        if (
            new_x >= Field.MARGIN and
            new_x + self.rect.width <= Screen.WIDTH - Field.MARGIN
        ):
            self.pos[0] = new_x
        else:
            self.velocity = [0.0, 0.0]

        if (
            new_y >= Field.MARGIN and
            new_y + self.rect.height <= Screen.HEIGHT - Field.MARGIN
        ):
            self.pos[1] = new_y
        else:
            self.velocity = [0.0, 0.0]

        self.rect.x = int(self.pos[0])
        self.rect.y = int(self.pos[1])

        # keep rotated rect/mask centered on new position
        self.update_sprite()

        # rotated collision
        if self.collides_with_player(other):
            self.pos = old_pos
            self.rect.center = old_center
            self.velocity = [0.0, 0.0]
            self.update_sprite()

    def draw(self, surface) -> None:
        """Draw the rotated player"""
        surface.blit(self.image, self.rotated_rect.topleft)

        center = self.rotated_rect.center
        line_length = 30
        end_pos = (
            center[0] + int(self.direction[0] * line_length),
            center[1] + int(self.direction[1] * line_length)
        )
        pygame.draw.line(surface, (255, 0, 0), center, end_pos, 3)
