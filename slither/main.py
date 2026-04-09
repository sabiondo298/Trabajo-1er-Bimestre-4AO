import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()
try:
    pygame.mixer.init()
    audio_available = True
except pygame.error:
    print("Audio not available. Running without sound.")
    audio_available = False

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
SNAKE_SPEED = 3
FOOD_SIZE = 5
INITIAL_SNAKE_SIZE = 10
MAX_FOOD = 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Player colors
PLAYER_COLORS = [GREEN, BLUE, YELLOW, PURPLE]

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slither.io Clone")
clock = pygame.time.Clock()

# Load sounds (we'll add sound files later)
if audio_available:
    try:
        eat_sound = pygame.mixer.Sound('eat.wav')
        death_sound = pygame.mixer.Sound('death.wav')
        background_music = pygame.mixer.Sound('background.wav')
        background_music.play(-1)  # Loop background music
    except:
        print("Sound files not found. Running without sound.")
        eat_sound = None
        death_sound = None
        background_music = None
else:
    eat_sound = None
    death_sound = None
    background_music = None

class Snake:
    def __init__(self, x, y, color, is_ai=False):
        self.body = [(x, y)]
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.color = color
        self.score = 0
        self.alive = True
        self.is_ai = is_ai
        self.target_food = None

    def move(self):
        if not self.alive:
            return

        head = self.body[0]
        dx, dy = self.direction

        # Calculate new head position
        new_head = (head[0] + dx * SNAKE_SPEED, head[1] + dy * SNAKE_SPEED)

        # Wrap around screen edges
        new_head = (new_head[0] % WIDTH, new_head[1] % HEIGHT)

        self.body.insert(0, new_head)

        # Remove tail unless growing
        if len(self.body) > INITIAL_SNAKE_SIZE + self.score:
            self.body.pop()

    def grow(self):
        self.score += 1

    def draw(self, screen):
        if not self.alive:
            return

        for i, segment in enumerate(self.body):
            # Make head slightly larger and different color
            size = FOOD_SIZE + 2 if i == 0 else FOOD_SIZE
            color = self.color if i == 0 else tuple(max(0, c - 50) for c in self.color)
            pygame.draw.circle(screen, color, (int(segment[0]), int(segment[1])), size)

    def check_collision(self, other_snakes, food_list):
        if not self.alive:
            return

        head = self.body[0]

        # Check collision with other snakes
        for snake in other_snakes:
            if snake == self or not snake.alive:
                continue

            for i, segment in enumerate(snake.body):
                distance = math.hypot(head[0] - segment[0], head[1] - segment[1])
                if distance < FOOD_SIZE + 5:
                    # If hitting another snake's head and you're bigger, you can eat them
                    if i == 0:  # Head collision
                        if len(self.body) > len(snake.body) * 1.2:  # You must be significantly bigger
                            snake.alive = False
                            self.score += snake.score // 2  # Gain half their score
                            if death_sound:
                                death_sound.play()
                        elif len(snake.body) > len(self.body) * 1.2:
                            # They eat you
                            self.alive = False
                            snake.score += self.score // 2
                            if death_sound:
                                death_sound.play()
                    else:  # Body collision - always deadly
                        self.alive = False
                        if death_sound:
                            death_sound.play()
                    return

        # Check collision with food
        for food in food_list[:]:
            if math.hypot(head[0] - food[0], head[1] - food[1]) < FOOD_SIZE + 5:
                food_list.remove(food)
                self.grow()
                if eat_sound:
                    eat_sound.play()

    def ai_move(self, food_list, all_snakes):
        if not self.is_ai or not self.alive:
            return

        head = self.body[0]

        # Find closest food
        closest_food = None
        min_distance = float('inf')
        for food in food_list:
            distance = math.hypot(head[0] - food[0], head[1] - food[1])
            if distance < min_distance:
                min_distance = distance
                closest_food = food

        if closest_food:
            # Check for dangerous snakes nearby
            danger_close = False
            for snake in all_snakes:
                if snake == self or not snake.alive:
                    continue
                if len(snake.body) > len(self.body) * 1.1:  # Bigger snake is dangerous
                    snake_head = snake.body[0]
                    distance_to_danger = math.hypot(head[0] - snake_head[0], head[1] - snake_head[1])
                    if distance_to_danger < 100:  # Dangerously close
                        danger_close = True
                        # Move away from danger
                        dx = head[0] - snake_head[0]
                        dy = head[1] - snake_head[1]
                        distance = math.hypot(dx, dy)
                        if distance > 0:
                            self.direction = (dx / distance, dy / distance)
                        break

            if not danger_close:
                # Move towards closest food
                dx = closest_food[0] - head[0]
                dy = closest_food[1] - head[1]
                distance = math.hypot(dx, dy)

                if distance > 0:
                    self.direction = (dx / distance, dy / distance)
        else:
            # Random movement if no food, but try to avoid danger
            danger_nearby = False
            for snake in all_snakes:
                if snake == self or not snake.alive:
                    continue
                if len(snake.body) > len(self.body):
                    snake_head = snake.body[0]
                    distance_to_danger = math.hypot(head[0] - snake_head[0], head[1] - snake_head[1])
                    if distance_to_danger < 80:
                        danger_nearby = True
                        # Move away from danger
                        dx = head[0] - snake_head[0]
                        dy = head[1] - snake_head[1]
                        distance = math.hypot(dx, dy)
                        if distance > 0:
                            self.direction = (dx / distance, dy / distance)
                        break

            if not danger_nearby and random.random() < 0.02:  # Change direction occasionally
                self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

def create_food():
    return (random.randint(0, WIDTH), random.randint(0, HEIGHT))

def draw_score(screen, snakes):
    font = pygame.font.Font(None, 36)
    for i, snake in enumerate(snakes):
        if snake.alive:
            player_type = "AI" if snake.is_ai else "Human"
            score_text = font.render(f"Player {i+1} ({player_type}): {snake.score}", True, snake.color)
            screen.blit(score_text, (10, 10 + i * 40))

def draw_game_over(screen, snakes):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    # Game Over text
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)

    game_over_text = font_large.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 150))

    # Leaderboard
    leaderboard_text = font_medium.render("Final Scores:", True, WHITE)
    screen.blit(leaderboard_text, (WIDTH//2 - leaderboard_text.get_width()//2, HEIGHT//2 - 80))

    # Sort snakes by score
    sorted_snakes = sorted(snakes, key=lambda s: s.score, reverse=True)

    for i, snake in enumerate(sorted_snakes):
        player_type = "AI" if snake.is_ai else "Human"
        color_name = ["Green", "Blue", "Yellow", "Purple"][PLAYER_COLORS.index(snake.color)]
        score_text = font_small.render(f"{i+1}. {color_name} ({player_type}): {snake.score}", True, snake.color)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 40 + i * 30))

    # Restart instruction
    restart_text = font_small.render("Press R to restart or ESC to quit", True, WHITE)
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT - 50))

def main():
    # Create players
    snakes = []
    num_players = 4  # Can be changed to 1-4

    for i in range(num_players):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        is_ai = i >= 1  # First player is human, others are AI
        snakes.append(Snake(x, y, PLAYER_COLORS[i], is_ai))

    food_list = [create_food() for _ in range(50)]

    running = True
    game_over = False

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    # Restart game
                    return main()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if not game_over:
            # Handle player input
            keys = pygame.key.get_pressed()

            # Player 1 controls (WASD)
            if not snakes[0].is_ai and snakes[0].alive:
                if keys[pygame.K_a]:
                    snakes[0].direction = (-1, 0)
                elif keys[pygame.K_d]:
                    snakes[0].direction = (1, 0)
                elif keys[pygame.K_w]:
                    snakes[0].direction = (0, -1)
                elif keys[pygame.K_s]:
                    snakes[0].direction = (0, 1)

            # Player 2 controls (Arrow keys)
            if len(snakes) > 1 and not snakes[1].is_ai and snakes[1].alive:
                if keys[pygame.K_LEFT]:
                    snakes[1].direction = (-1, 0)
                elif keys[pygame.K_RIGHT]:
                    snakes[1].direction = (1, 0)
                elif keys[pygame.K_UP]:
                    snakes[1].direction = (0, -1)
                elif keys[pygame.K_DOWN]:
                    snakes[1].direction = (0, 1)

            # Player 3 controls (IJKL)
            if len(snakes) > 2 and not snakes[2].is_ai and snakes[2].alive:
                if keys[pygame.K_j]:
                    snakes[2].direction = (-1, 0)
                elif keys[pygame.K_l]:
                    snakes[2].direction = (1, 0)
                elif keys[pygame.K_i]:
                    snakes[2].direction = (0, -1)
                elif keys[pygame.K_k]:
                    snakes[2].direction = (0, 1)

            # Player 4 controls (Numpad)
            if len(snakes) > 3 and not snakes[3].is_ai and snakes[3].alive:
                if keys[pygame.K_KP4]:
                    snakes[3].direction = (-1, 0)
                elif keys[pygame.K_KP6]:
                    snakes[3].direction = (1, 0)
                elif keys[pygame.K_KP8]:
                    snakes[3].direction = (0, -1)
                elif keys[pygame.K_KP5]:
                    snakes[3].direction = (0, 1)

            # AI movement
            for snake in snakes:
                if snake.is_ai:
                    snake.ai_move(food_list, snakes)

            # Move all snakes
            for snake in snakes:
                snake.move()

            # Check collisions
            for snake in snakes:
                snake.check_collision(snakes, food_list)

            # Spawn new food
            while len(food_list) < MAX_FOOD:
                food_list.append(create_food())

            # Check if all human players are dead
            human_alive = any(not snake.is_ai and snake.alive for snake in snakes)
            if not human_alive:
                game_over = True

        # Draw everything
        screen.fill(BLACK)

        # Draw food
        for food in food_list:
            pygame.draw.circle(screen, RED, (int(food[0]), int(food[1])), FOOD_SIZE)

        # Draw snakes
        for snake in snakes:
            snake.draw(screen)

        # Draw scores
        draw_score(screen, snakes)

        # Draw game over screen if needed
        if game_over:
            draw_game_over(screen, snakes)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
