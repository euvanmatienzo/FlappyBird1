import pygame
import random
import sys

pygame.init()

# Load and play background music
pygame.mixer.music.load("background.wav")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# Load sounds
hover_sound = pygame.mixer.Sound("hover.wav")
click_sound = pygame.mixer.Sound("click.wav")
point_sound = pygame.mixer.Sound("point.wav")

# Load UFO image
ufo_image = pygame.image.load("ufo.png")
ufo_image = pygame.transform.scale(ufo_image, (40, 40))  # Adjust size if needed

# Screen
WIDTH, HEIGHT = 400, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UFO Escape")

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 200, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

# Game constants
gravity = 0.5
pipe_gap = 150
pipe_velocity = 3
pipe_width = 60

# Bird
bird = pygame.Rect(50, HEIGHT // 2, 30, 30)

# Button class
class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.hovered = False

    def draw(self, surface, mouse_pos):
        is_hover = self.rect.collidepoint(mouse_pos)
        if is_hover and not self.hovered:
            hover_sound.play()
        self.hovered = is_hover

        color = WHITE if is_hover else LIGHT_GRAY
        pygame.draw.rect(surface, color, self.rect)
        draw_text(self.text, small_font, BLACK, surface, self.rect.centerx, self.rect.centery)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            click_sound.play()
            self.callback()

# Utilities
def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Create a pipe pair and track if passed
def create_pipe():
    height = random.randint(100, 400)
    top_pipe = pygame.Rect(WIDTH, 0, pipe_width, height)
    bottom_pipe = pygame.Rect(WIDTH, height + pipe_gap, pipe_width, HEIGHT - (height + pipe_gap))
    return {"top": top_pipe, "bottom": bottom_pipe, "passed": False}

def main_game():
    global high_score
    bird.y = HEIGHT // 2
    bird_movement = 0
    score = 0
    pipes = []

    clock = pygame.time.Clock()
    spawn_pipe = pygame.USEREVENT
    pygame.time.set_timer(spawn_pipe, 1500)

    running = True
    while running:
        clock.tick(60)
        win.fill(BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == spawn_pipe:
                pipes.append(create_pipe())

        # Handle input
        mouse_pressed = pygame.mouse.get_pressed()[0]
        keys = pygame.key.get_pressed()
        if mouse_pressed or keys[pygame.K_SPACE]:
            bird_movement = -8

        bird_movement += gravity
        bird.y += int(bird_movement)

        # Draw UFO instead of  rectangle
        win.blit(ufo_image, bird)

        for pipe_data in pipes:
            pipe_data["top"].x -= pipe_velocity
            pipe_data["bottom"].x -= pipe_velocity

            pygame.draw.rect(win, GREEN, pipe_data["top"])
            pygame.draw.rect(win, GREEN, pipe_data["bottom"])

            # Check scoring
            if not pipe_data["passed"] and pipe_data["top"].right < bird.left:
                pipe_data["passed"] = True
                score += 1
                point_sound.play()

        # Remove off-screen pipes
        pipes = [p for p in pipes if p["top"].right > 0]

        # Collision detection
        for pipe_data in pipes:
            if bird.colliderect(pipe_data["top"]) or bird.colliderect(pipe_data["bottom"]):
                return score

        if bird.top <= 0 or bird.bottom >= HEIGHT:
            return score

        draw_text(str(score), font, WHITE, win, WIDTH // 2, 50)
        pygame.display.update()

def game_over_screen(score, high_score):
    win.fill(BLUE)
    draw_text("Game Over", font, WHITE, win, WIDTH // 2, HEIGHT // 4)
    draw_text(f"Score: {score}", small_font, WHITE, win, WIDTH // 2, HEIGHT // 2)
    draw_text(f"Best: {high_score}", small_font, WHITE, win, WIDTH // 2, HEIGHT // 2 + 40)
    draw_text("Click or Press SPACE to Restart", small_font, WHITE, win, WIDTH // 2, HEIGHT - 60)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

def about_screen():
    win.fill(BLUE)
    draw_text("About", font, WHITE, win, WIDTH // 2, HEIGHT // 4)
    draw_text("Developer:", small_font, WHITE, win, WIDTH // 2, HEIGHT // 2)
    draw_text("Marl Euvan Matienzo", small_font, WHITE, win, WIDTH // 2, HEIGHT // 2 + 40)
    draw_text("Click anywhere to return", small_font, WHITE, win, WIDTH // 2, HEIGHT - 50)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

def menu_screen():
    selected_action = [None]

    def start_game():
        selected_action[0] = "start"

    def show_about():
        about_screen()

    def quit_game():
        pygame.quit()
        sys.exit()

    buttons = [
        Button("Start", WIDTH//2 - 75, 250, 150, 40, start_game),
        Button("About", WIDTH//2 - 75, 310, 150, 40, show_about),
        Button("Quit", WIDTH//2 - 75, 370, 150, 40, quit_game),
    ]

    while selected_action[0] is None:
        win.fill(BLUE)
        draw_text("UFO Escape", font, WHITE, win, WIDTH // 2, 100)

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.draw(win, mouse_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    button.check_click(mouse_pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start_game()

    return selected_action[0]
#Test
# Game loop
high_score = 0
while True:
    choice = menu_screen()
    if choice == "start":
        score = main_game()
        if score > high_score:
            high_score = score
        game_over_screen(score, high_score)
