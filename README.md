# Slither.io Clone

A simple recreation of the popular game Slither.io using Pygame.

## Features

- **Multiplayer**: Support for up to 4 local players
- **AI Snakes**: Computer-controlled snakes that compete with players
- **Scoring System**: Points awarded for eating food
- **Smooth Controls**: Responsive movement for all players
- **Collision Detection**: Realistic snake collisions
- **Sound Effects**: Audio feedback (when sound files are available)

## Controls

### Player 1 (Green Snake)
- W: Move Up
- A: Move Left
- S: Move Down
- D: Move Right

### Player 2 (Blue Snake - AI by default)
- ↑: Move Up
- ←: Move Left
- ↓: Move Down
- →: Move Right

### Player 3 (Yellow Snake - AI by default)
- I: Move Up
- J: Move Left
- K: Move Down
- L: Move Right

### Player 4 (Purple Snake - AI by default)
- Numpad 8: Move Up
- Numpad 4: Move Left
- Numpad 5: Move Down
- Numpad 6: Move Right

## How to Play

1. Control your snake to eat the red food pellets
2. Your snake grows longer as you eat more food
3. Avoid colliding with other snakes
4. The game continues until all human players die
5. Try to get the highest score!

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Install Pygame:
   ```
   pip install pygame
   ```

2. Run the game:
   ```
   python slither/main.py
   ```

## Sound Effects

To enable sound effects, add the following WAV files to the slither/ directory:
- `eat.wav`: Sound when eating food
- `death.wav`: Sound when a snake dies
- `background.wav`: Background music

## Customization

You can modify the following constants in slither/main.py:
- `WIDTH`, `HEIGHT`: Screen dimensions
- `FPS`: Game speed
- `SNAKE_SPEED`: How fast snakes move
- `MAX_FOOD`: Maximum number of food pellets
- `num_players`: Number of players (1-4)