# Rocket League

A small two-player soccer game built with Python and Pygame. Players drive cars around a field, hit the ball into the opposing goal, and race to be the first to 5 goals.

## Requirements

- Python 3
- Pygame

Install Pygame if needed:

```sh
python3 -m pip install pygame
```

## Run

From the project directory:

```sh
python3 main.py
```

## Controls

Player 1:

- Up Arrow: drive forward
- Down Arrow: reverse
- Left Arrow / Right Arrow: turn

Player 2:

- W: drive forward
- S: reverse
- A / D: turn

Press Enter or Space to start or restart a match.

## Project Structure

- `main.py`: game loop, scoring, menus, and collision resolution
- `player.py`: player movement, sprite rotation, and player collision helpers
- `ball.py`: ball state, movement, and rendering
- `constants.py`: screen, field, control, player, and asset configuration
- `sprites/`: car and ball sprite assets

## Sprite Credits

- Ball sprite: "Sport Balls Pixel-Art Pack." Itch.io, 2023, beemaxstudio.itch.io/sport-balls-pixel-pack. Accessed 27 Apr. 2026.
- Car sprites: "Sports Car Set [Game Assets]." Itch.io, 2026, sundae-buoy.itch.io/16bit-race-car-set. Accessed 27 Apr. 2026.
