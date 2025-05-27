import pygame
import sys
import time
# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fun Run 3 Pixel-Collision")

# Clock
clock = pygame.time.Clock()
FPS = 60

# World dimensions (must match your image width)
MAP_LENGTH = 3000

# Load & scale background
bg = pygame.image.load("map.png").convert()
bg = pygame.transform.scale(bg, (MAP_LENGTH, SCREEN_HEIGHT))

# Exact ground color in the image (RGBA)
GROUND_COLOR = (0, 0, 0, 255)

# Player state in world coordinates
player_world_x = 150
player_y = 200
PLAYER_W, PLAYER_H = 50, 50

# Physics
vel_y = 0
GRAVITY = 1
JUMP_STRENGTH = -15
on_ground = False

# Scroll offset
scroll_x = 0

def draw():
    # Draw the scrolling background
    screen.blit(bg, (-scroll_x, 0))
    # Draw the player at center X
    pygame.draw.rect(
        screen,
        (255, 50, 50),
        (SCREEN_WIDTH // 2, player_y, PLAYER_W, PLAYER_H)
    )

# Main game loop
running = True
while running:
    clock.tick(FPS)
    #time.sleep(0.3)
    keys = pygame.key.get_pressed()
    # 1) Determine desired horizontal movement
    desired_dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5

    # 2) Determine desired vertical movement
    if keys[pygame.K_SPACE] and on_ground:
        vel_y = JUMP_STRENGTH
        on_ground = False
    vel_y += GRAVITY
    desired_dy = vel_y

    # 3) Recompute scroll
    scroll_x = max(0, min(player_world_x - SCREEN_WIDTH // 2,
                          MAP_LENGTH - SCREEN_WIDTH))


    # Helper to sample a pixel in world coords
    def sample_world_pixel(wx, wy):
        sx = int(wx - scroll_x)
        sy = int(wy)
        if 0 <= sx < MAP_LENGTH and 0 <= sy < SCREEN_HEIGHT:
            return bg.get_at((sx, sy))
        return SKY_COLOR  # off-map treated as sky


    SKY_COLOR = bg.get_at((0, 0))  # assume top-left is sky

    # 4) Horizontal collision check (left/right)
    if desired_dx != 0:
        step = 1 if desired_dx > 0 else -1
        blocked_h = False
        for dy in range(0, PLAYER_H, 5):  # sample every 5px vertically
            # sample at the side the player is moving toward
            foot_wx = player_world_x + (PLAYER_W if step > 0 else 0)
            sample_x = foot_wx + desired_dx
            sample_y = player_y + dy
            #print(sample_y)
            if sample_world_pixel(sample_x, sample_y) == GROUND_COLOR:
                blocked_h = True
                break
        if not blocked_h:
            print('hi')
            player_world_x += desired_dx

    # 5) Vertical collision check (up/down)
    blocked_v = False
    if desired_dy != 0:
        step = 1 if desired_dy > 0 else -1
        for dx in range(0, PLAYER_W, 5):  # sample every 5px horizontally
            # sample at top or bottom edge
            sample_x = player_world_x + dx + PLAYER_W // 2
            sample_y = player_y + (PLAYER_H if step > 0 else 0) + desired_dy
            print(sample_y)
            if sample_world_pixel(sample_x, sample_y) == GROUND_COLOR:
                # block and snap
                if step > 0:
                    # landing on ground
                    player_y = sample_y - PLAYER_H - 1
                    on_ground = True
                else:
                    # hitting ceiling
                    player_y = sample_y + 1
                vel_y = 0
                blocked_v = True
                break
        if not blocked_v:
            player_y += desired_dy
            on_ground = False

    draw()
    pygame.display.flip()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
