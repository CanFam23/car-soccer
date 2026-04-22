import pygame
from constants import Field, Screen


class Ball:
    def __init__(self, x: int, y: int, radius: int, color: tuple[int, int, int]) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = 0
        self.vy = 0
        self.friction = 0.98

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction
        if abs(self.vx) < 0.1:
            self.vx = 0
        if abs(self.vy) < 0.1:
            self.vy = 0
            
        # Bounce off boundaries
        if self.x - self.radius < Field.MARGIN:
            self.x = Field.MARGIN + self.radius
            self.vx = -self.vx
        elif self.x + self.radius > Screen.WIDTH - Field.MARGIN:
            self.x = Screen.WIDTH - Field.MARGIN - self.radius
            self.vx = -self.vx
        if self.y - self.radius < Field.MARGIN:
            self.y = Field.MARGIN + self.radius
            self.vy = -self.vy
        elif self.y + self.radius > Screen.HEIGHT - Field.MARGIN:
            self.y = Screen.HEIGHT - Field.MARGIN - self.radius
            self.vy = -self.vy

    def draw(self, surface) -> None:
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
