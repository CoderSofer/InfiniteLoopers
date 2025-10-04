# Import and initialize the pygame library
import pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GREEN =  (167, 255, 100)
WHITE = (0, 0, 0)
BLACK = (255, 255, 255)
PINKYRED = (255, 100, 98)
RED = (255, 0, 0)

ROWS, COLS = 3, 3
TILE_SIZE = 120
GAP = 8

grid_w = COLS * TILE_SIZE + (COLS - 1) * GAP
grid_h = ROWS * TILE_SIZE + (ROWS - 1) * GAP
start_x = (SCREEN_WIDTH  - grid_w) // 2
start_y = (SCREEN_HEIGHT - grid_h) // 2


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True


# Each tile
class Tile(pygame.sprite.Sprite):
        def __init__(self, row, col, start_x, start_y, tile_size, gap, label="Empty", color=PINKYRED):
            super().__init__()
            self.row, self.col = row, col
            self.label = label
            self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
			
			# Positioning
            self.rect = self.image.get_rect()
            x = start_x + col * (tile_size + gap)
            y = start_y + row * (tile_size + gap)
            self.rect.topleft = (x, y)
            
			# Drawing
            self.image.fill((0, 0, 0, 0))  
            pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=12)
            pygame.draw.rect(self.image, (220, 235, 245), self.image.get_rect(), width=2, border_radius=12)
            
        # Some logic
        def update(self):
              pass 

            

allTileList = pygame.sprite.Group()

# Add tiles to tile list
for r in range(ROWS):
    for c in range(COLS):
        allTileList.add(Tile(r, c, start_x, start_y, TILE_SIZE, GAP, label=f"Tile {r},{c}"))


# Main loop
while running:
    # Look at every event in the queue
    for event in pygame.event.get():
        # Quit cases
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    #Looping through this 
    screen.fill(GREEN)
    allTileList.update()
    allTileList.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
