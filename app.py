import pygame
import random
import sys
import os

# --- Game Configuration ---
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 712
FPS = 60

# Bird properties
BIRD_X_POS = 50
BIRD_START_Y_POS = SCREEN_HEIGHT // 2
GRAVITY = 0.25
FLAP_STRENGTH = -7
BIRD_ROTATION_SPEED = 3
MAX_UPWARD_ROTATION = 25
MAX_DOWNWARD_ROTATION = -90
BIRD_TARGET_SIZE = (34, 24)

# Pipe properties
PIPE_GAP = 130
PIPE_FREQUENCY = 1500
PIPE_SPEED = 2
# PIPE_HEIGHT_RANGE now defines the height of the top pipe,
# which is also the y-coordinate where the gap begins.
# Min height of top pipe: 100 (gap starts at y=100)
# Max height of top pipe: SCREEN_HEIGHT - PIPE_GAP - 100 (ensures bottom pipe has at least 100px visible before ground)
MIN_TOP_PIPE_HEIGHT = 100 # Min y-value for the bottom of the top pipe
MAX_TOP_PIPE_HEIGHT = SCREEN_HEIGHT - PIPE_GAP - 100 # Max y-value for the bottom of the top pipe
PIPE_TOP_HEIGHT_RANGE = (MIN_TOP_PIPE_HEIGHT, MAX_TOP_PIPE_HEIGHT) 

PIPE_TARGET_SIZE = (52, 320) # Size of the pipe *segment* image

# Ground properties
GROUND_Y = SCREEN_HEIGHT - 100
GROUND_SPEED = PIPE_SPEED
GROUND_TARGET_HEIGHT = 100
GROUND_TARGET_SIZE = (SCREEN_WIDTH, GROUND_TARGET_HEIGHT)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)

# --- Asset Loading ---
def load_image(filename, target_size=None, use_fallback=True, fallback_color=None, fallback_dimensions=None):
    try:
        image_path = filename
        image = pygame.image.load(image_path)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        if target_size:
            image = pygame.transform.scale(image, target_size)
        return image
    except pygame.error as e:
        print(f"Cannot load image: {filename} - {e}")
        if use_fallback:
            print("Using fallback surface.")
            if fallback_dimensions and fallback_color:
                fallback_surface = pygame.Surface(fallback_dimensions)
                fallback_surface.fill(fallback_color)
                return fallback_surface
            fallback_surface = pygame.Surface([30,30]); fallback_surface.fill(WHITE); return fallback_surface
        sys.exit()

# --- Game Classes ---
class Bird(pygame.sprite.Sprite):
    def __init__(self, image_surface):
        super().__init__()
        self.original_image = image_surface
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(BIRD_X_POS, BIRD_START_Y_POS))
        self.velocity_y = 0
        self.rotation = 0

    def flap(self):
        self.velocity_y = FLAP_STRENGTH
        self.rotation = MAX_UPWARD_ROTATION

    def update(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        if self.velocity_y < 0: self.rotation += BIRD_ROTATION_SPEED * 2
        elif self.velocity_y > 1: self.rotation -= BIRD_ROTATION_SPEED
        self.rotation = max(MAX_DOWNWARD_ROTATION, min(MAX_UPWARD_ROTATION, self.rotation))
        self.image = pygame.transform.rotozoom(self.original_image, self.rotation, 1)
        current_center = self.rect.center
        self.rect = self.image.get_rect(center=current_center)
        if self.rect.top < 0: self.rect.top = 0; self.velocity_y = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y_param, pipe_segment_surface, is_top=True):
        super().__init__()
        self.pipe_segment_surface = pipe_segment_surface
        self.is_top_pipe = is_top # For scoring
        self.passed = False

        segment_width = self.pipe_segment_surface.get_width()
        segment_height = self.pipe_segment_surface.get_height()

        if self.is_top_pipe:
            # y_param is the height of the top pipe (gap starts at this y-coordinate from top)
            top_pipe_height = y_param
            # Ensure height is at least 1 to avoid Surface error, though range should prevent this
            top_pipe_height = max(1, top_pipe_height) 

            self.image = pygame.Surface((segment_width, top_pipe_height), pygame.SRCALPHA)
            self.image.fill((0,0,0,0)) # Transparent background

            flipped_segment = pygame.transform.flip(self.pipe_segment_surface, False, True)
            
            # Tile the flipped segment onto self.image, aligning to its bottom
            # The self.image is (segment_width, top_pipe_height)
            # We blit the flipped_segment onto it such that flipped_segment's bottom aligns with self.image's bottom
            # The y-coordinate for blitting is relative to self.image's top-left (0,0)
            # If top_pipe_height < segment_height, we blit at y = top_pipe_height - segment_height
            # This effectively crops from the bottom of the flipped_segment.
            
            # Tiling logic (simplified as top_pipe_height is usually < segment_height with current settings)
            y_blit_target_on_self_image = top_pipe_height # Start at the bottom of self.image
            while y_blit_target_on_self_image > 0:
                current_segment_top_on_self_image = y_blit_target_on_self_image - segment_height
                self.image.blit(flipped_segment, (0, current_segment_top_on_self_image))
                y_blit_target_on_self_image -= segment_height
                if segment_height <= 0: break # Safety for 0-height segments

            self.rect = self.image.get_rect(topleft=(x, 0))
        else:
            # y_param is the y-coordinate where the top pipe ended (bottom of top pipe)
            # Bottom pipe starts below this, after the gap
            bottom_pipe_y_start = y_param + PIPE_GAP
            self.image = self.pipe_segment_surface # Use the standard segment
            self.rect = self.image.get_rect(topleft=(x, bottom_pipe_y_start))

    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Ground(pygame.sprite.Sprite):
    def __init__(self, y_pos, image_surface1, image_surface2=None):
        super().__init__()
        self.image1 = image_surface1
        self.rect1 = self.image1.get_rect(topleft=(0, y_pos))
        self.image2 = image_surface2 if image_surface2 else self.image1
        self.rect2 = self.image2.get_rect(topleft=(self.rect1.width, y_pos))
        self.y_pos = y_pos

    def update(self):
        self.rect1.x -= GROUND_SPEED; self.rect2.x -= GROUND_SPEED
        if self.rect1.right <= 0: self.rect1.left = self.rect2.right
        if self.rect2.right <= 0: self.rect2.left = self.rect1.right
            
    def draw(self, screen):
        screen.blit(self.image1, self.rect1); screen.blit(self.image2, self.rect2)

# --- Game Functions ---
def create_pipe_pair(pipe_base_surface):
    # top_pipe_height_val is the y-coordinate where the gap starts, and also the height of the top pipe.
    top_pipe_height_val = random.randint(PIPE_TOP_HEIGHT_RANGE[0], PIPE_TOP_HEIGHT_RANGE[1])
    
    # For top pipe, pass its height.
    top_pipe = Pipe(SCREEN_WIDTH + 50, top_pipe_height_val, pipe_base_surface, is_top=True)
    # For bottom pipe, pass the y-coordinate where the top pipe ended.
    bottom_pipe = Pipe(SCREEN_WIDTH + 50, top_pipe_height_val, pipe_base_surface, is_top=False)
    return top_pipe, bottom_pipe

def display_score(screen, score, font):
    score_surface = font.render(f"Score: {score}", True, WHITE)
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
    screen.blit(score_surface, score_rect)

def display_message(screen, message, font, y_offset=0):
    text_surface = font.render(message, True, WHITE)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)

# --- Main Game Logic ---
def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Python")
    clock = pygame.time.Clock()

    bird_surface = load_image("bird.png", BIRD_TARGET_SIZE, True, BLUE, BIRD_TARGET_SIZE)
    pipe_segment_asset = load_image("pipe.png", PIPE_TARGET_SIZE, True, GREEN, PIPE_TARGET_SIZE) # This is the pipe *segment*
    bg_surface = load_image("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT), False)
    ground_surface = load_image("ground.png", GROUND_TARGET_SIZE, True, BROWN, GROUND_TARGET_SIZE)
    bg_color_fallback = (135, 206, 235)

    bird = Bird(bird_surface)
    bird_group = pygame.sprite.GroupSingle(bird)
    pipe_group = pygame.sprite.Group()
    ground = Ground(GROUND_Y, ground_surface)
    
    score = 0; high_score = 0
    try: game_font = pygame.font.Font(None, 40)
    except: game_font = pygame.font.SysFont("arial", 30)

    pipe_spawn_timer = pygame.USEREVENT
    pygame.time.set_timer(pipe_spawn_timer, PIPE_FREQUENCY)

    running = True; game_active = False; game_over_state = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_active and not game_over_state: # Start
                        game_active = True; bird.rect.center = (BIRD_X_POS, BIRD_START_Y_POS)
                        bird.velocity_y = 0; bird.rotation = 0; pipe_group.empty(); score = 0
                    elif game_active: bird.flap()
                    elif game_over_state: # Restart
                        game_active = True; game_over_state = False
                        bird.rect.center = (BIRD_X_POS, BIRD_START_Y_POS); bird.velocity_y = 0
                        bird.rotation = 0; pipe_group.empty(); score = 0
                if event.key == pygame.K_ESCAPE: running = False
            if event.type == pipe_spawn_timer and game_active:
                top_p, bottom_p = create_pipe_pair(pipe_segment_asset)
                pipe_group.add(top_p); pipe_group.add(bottom_p)

        if game_active:
            bird_group.update(); pipe_group.update(); ground.update()

            if pygame.sprite.spritecollide(bird, pipe_group, False, pygame.sprite.collide_mask) or \
               bird.rect.bottom >= GROUND_Y:
                game_active = False; game_over_state = True
                if bird.rect.bottom >= GROUND_Y: bird.rect.bottom = GROUND_Y; bird.velocity_y = 0
                if score > high_score: high_score = score
            
            if bird.rect.top <= 0 : bird.rect.top = 0 # Already handled in bird.update too

            # Scoring
            for p in pipe_group:
                if not p.passed and p.rect.right < bird.rect.left:
                    if p.is_top_pipe: # Score for passing a top pipe (or could be bottom)
                        p.passed = True
                        score += 1
                        # To mark its pair as passed (if needed for other logic, not strictly for scoring):
                        # This would require finding the pair, e.g., by x-coordinate and is_top_pipe status.
                        # For simple scoring, marking one of the pair is enough.

        # Drawing
        if bg_surface: screen.blit(bg_surface, (0,0))
        else: screen.fill(bg_color_fallback)
        pipe_group.draw(screen)
        ground.draw(screen)
        bird_group.draw(screen)
        display_score(screen, score, game_font)

        if not game_active and not game_over_state:
            display_message(screen, "Flappy Python", game_font, -50)
            display_message(screen, "Press SPACE to Start", game_font)
        elif game_over_state:
            display_message(screen, "GAME OVER!", game_font, -50)
            display_message(screen, f"Score: {score}", game_font, 0)
            display_message(screen, f"High Score: {high_score}", game_font, 40)
            display_message(screen, "Press SPACE to Restart", game_font, 80)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()