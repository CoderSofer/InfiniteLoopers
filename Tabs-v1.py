import pygame
pygame.init()

# --- Grid setup ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ROWS, COLS = 3, 3
TILE_SIZE = 120
GAP = 12
TILE_COLOUR = (0,0,0)
BACKGROUND_COLOR = (142, 214, 88)
TAB_BUTTON_COLOR = (255, 100, 98)
TAB_BUTTON_COLOR_ACTIVE = (255, 100+30, 98+10)
grid_w = COLS * TILE_SIZE + (COLS - 1) * GAP
grid_h = ROWS * TILE_SIZE + (ROWS - 1) * GAP
start_x = (SCREEN_WIDTH  - grid_w) // 2
start_y = (SCREEN_HEIGHT - grid_h) // 2

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Farm Game")
tab_font = pygame.font.SysFont(None, 24)

# --- Tab options ---
num_soils = 5
soil_labels = ["Lose and well-draining", "Rich and well-draining", "Deep and Lose", "Loamy", "Well-draining"]
soil_colors = [
    (139, 69, 19), (160, 82, 45), (205, 133, 63), (222, 184, 135), (244, 164, 96)
]
num_plants = 5
plant_labels = ["Carrots", "Potatoes", "Tomatoes", "Cucumbers", "Lentils"]
plant_colors = [
    (237, 145, 33), (255,251,149), (255, 99, 71), (103,171,5), (126, 105, 95)
]
num_fertilisers = 3
fertiliser_labels = [f"Fertiliser{i+1}" for i in range(num_fertilisers)]
fertiliser_colors = [
    (255, 215, 0), (128, 128, 128), (255, 255, 255)
]

# --- Tile class ---
class Tile:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.x = start_x + col * (TILE_SIZE + GAP)
        self.y = start_y + row * (TILE_SIZE + GAP)
        self.rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        self.soil = None
        self.plant = None
        self.fertiliser = None
        self.plant_time = None  # When the plant was planted
        self.grown = False      # Is the plant grown?

    def update_growth(self, now):
        # Define allowed soils for each plant index
        allowed_soils = {
            0: [2],      # Carrots: Deep and Lose, Lose and well-draining
            1: [0],      # Potatoes: Lose and well-draining, Well-draining
            2: [1],      # Tomatoes: Rich and well-draining, Well-draining
            3: [3],         # Cucumbers: Loamy
            4: [4]          # Lentils: Well-draining
        }
        if self.plant is not None and self.plant_time is not None:
            # Only grow if soil is compatible
            if self.soil in allowed_soils.get(self.plant, []):
                if not self.grown and now - self.plant_time >= 10:
                    self.grown = True
            else:
                self.grown = False
        else:
            self.grown = False

    def draw(self, surf):
        # Fill
        fill = soil_colors[self.soil] if self.soil is not None else (TILE_COLOUR)
        pygame.draw.rect(surf, fill, self.rect, border_radius=12)
        # Plant outline
        if self.plant is not None:
            color = plant_colors[self.plant]
            pygame.draw.rect(surf, color, self.rect, 4, border_radius=12)
            # If grown, draw a yellow border inside to indicate harvestable
            if self.grown:
                inner_rect = self.rect.inflate(-12, -12)
                pygame.draw.rect(surf, (255, 215, 0), inner_rect, 4, border_radius=8)
        else:
            pygame.draw.rect(surf, (0, 0, 0), self.rect, 2, border_radius=12)
        # Fertiliser outer outline
        outer_rect = self.rect.inflate(8, 8)
        if self.fertiliser is not None:
            pygame.draw.rect(surf, fertiliser_colors[self.fertiliser], outer_rect, 4, border_radius=16)
        else:
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2, border_radius=16)

# --- Grid ---
tiles = [Tile(r, c) for r in range(ROWS) for c in range(COLS)]
selected_tile = None

# --- Tab popup state ---
tab_active = False
active_tab = "soil"
tab_width = 300
tab_button_width = 80
tab_button_height = 30
option_height = 20
option_width = 200
option_spacing = 3

import time

running = True
while running:
    now = time.time()
    screen.fill((BACKGROUND_COLOR))
    # Update growth for all tiles
    for tile in tiles:
        tile.update_growth(now)
        tile.draw(screen)

    # Draw tab popup for selected tile
    if tab_active and selected_tile is not None:
        tab_height = 120
        if active_tab == "soil":
            tab_height += num_soils * (option_height + option_spacing)
        elif active_tab == "plants":
            tab_height += num_plants * (option_height + option_spacing)
        elif active_tab == "fertiliser":
            tab_height += num_fertilisers * (option_height + option_spacing)
        if selected_tile.rect.right + 20 + tab_width > SCREEN_WIDTH:
            tab_x = selected_tile.rect.left - 20 - tab_width
        else:
            tab_x = selected_tile.rect.right + 20
        tab_y = selected_tile.rect.top
        tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
        pygame.draw.rect(screen, (220, 220, 220), tab_rect, border_radius=8)

        # Tab selection buttons
        soil_tab_btn_rect = pygame.Rect(tab_rect.x + 8, tab_rect.y + 8, tab_button_width, tab_button_height, border_radius=12)
        plants_tab_btn_rect = pygame.Rect(tab_rect.x + 8 + tab_button_width + 8, tab_rect.y + 8, tab_button_width, tab_button_height, border_radius=4)
        fertiliser_tab_btn_rect = pygame.Rect(tab_rect.x + 8 + 2 * (tab_button_width + 8), tab_rect.y + 8, tab_button_width, tab_button_height, border_radius=4)
        pygame.draw.rect(screen, (TAB_BUTTON_COLOR_ACTIVE) if active_tab == "soil" else (TAB_BUTTON_COLOR), soil_tab_btn_rect, border_radius=4)
        pygame.draw.rect(screen, (TAB_BUTTON_COLOR_ACTIVE) if active_tab == "plants" else (TAB_BUTTON_COLOR), plants_tab_btn_rect, border_radius=4)
        pygame.draw.rect(screen, (TAB_BUTTON_COLOR_ACTIVE) if active_tab == "fertiliser" else (TAB_BUTTON_COLOR), fertiliser_tab_btn_rect, border_radius=4)
        
        soil_btn_text = tab_font.render("Soil", True, (255, 255, 255))
        plants_btn_text = tab_font.render("Plants", True, (255, 255, 255))
        fertiliser_btn_text = tab_font.render("Fertiliser", True, (255, 255, 255))
        soil_btn_text_rect = soil_btn_text.get_rect(center=soil_tab_btn_rect.center)
        plant_btn_text_rect = plants_btn_text.get_rect(center=plants_tab_btn_rect.center)
        fertiliser_btn_text_rect = fertiliser_btn_text.get_rect(center=fertiliser_tab_btn_rect.center)
        screen.blit(soil_btn_text, soil_btn_text_rect)
        screen.blit(plants_btn_text, plant_btn_text_rect)
        screen.blit(fertiliser_btn_text, fertiliser_btn_text_rect)

        # Draw a close button (top right corner)
        close_size = 18
        close_rect = pygame.Rect(tab_rect.right - close_size - 8, tab_rect.y + 8, close_size, close_size)
        pygame.draw.rect(screen, (194, 43, 43), close_rect, border_radius=4)
        close_text = tab_font.render("x", True, (255, 255, 255))
        text_rect = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, text_rect)

        # Draw option buttons dynamically for active tab
        option_rects = []
        if active_tab == "soil":
            tab_text = tab_font.render("Choose your type of soil", True, (0, 0, 0))
            screen.blit(tab_text, (tab_rect.x + 8, tab_rect.y + tab_button_height + 16))
            for i, label in enumerate(soil_labels):
                option_rect = pygame.Rect(
                    tab_rect.x + 8,
                    tab_rect.y + tab_button_height + 40 + i * (option_height + option_spacing),
                    option_width,
                    option_height
                )
                option_rects.append(option_rect)
                pygame.draw.rect(screen, (100, 200, 100), option_rect)
                pygame.draw.rect(screen, (0, 0, 0), option_rect, 2)
                option_text = tab_font.render(label, True, (0, 0, 0))
                screen.blit(option_text, (option_rect.x + 2, option_rect.y + 2))
        elif active_tab == "plants":
            tab_text = tab_font.render("Choose your type of plant", True, (0, 0, 0))
            screen.blit(tab_text, (tab_rect.x + 8, tab_rect.y + tab_button_height + 16))
            for i, label in enumerate(plant_labels):
                option_rect = pygame.Rect(
                    tab_rect.x + 8,
                    tab_rect.y + tab_button_height + 40 + i * (option_height + option_spacing),
                    option_width,
                    option_height
                )
                option_rects.append(option_rect)
                pygame.draw.rect(screen, (100, 200, 100), option_rect)
                pygame.draw.rect(screen, (0, 0, 0), option_rect, 2)
                option_text = tab_font.render(label, True, (0, 0, 0))
                screen.blit(option_text, (option_rect.x + 2, option_rect.y + 2))
        elif active_tab == "fertiliser":
            tab_text = tab_font.render("Choose your fertiliser", True, (0, 0, 0))
            screen.blit(tab_text, (tab_rect.x + 8, tab_rect.y + tab_button_height + 16))
            for i, label in enumerate(fertiliser_labels):
                option_rect = pygame.Rect(
                    tab_rect.x + 8,
                    tab_rect.y + tab_button_height + 40 + i * (option_height + option_spacing),
                    option_width,
                    option_height
                )
                option_rects.append(option_rect)
                pygame.draw.rect(screen, (200, 200, 100), option_rect)
                pygame.draw.rect(screen, (0, 0, 0), option_rect, 2)
                option_text = tab_font.render(label, True, (0, 0, 0))
                screen.blit(option_text, (option_rect.x + 2, option_rect.y + 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not tab_active:
                # Check if a tile was clicked
                for tile in tiles:
                    if tile.rect.collidepoint(event.pos):
                        # If plant is grown, harvest it
                        if tile.plant is not None and tile.grown:
                            tile.plant = None
                            tile.plant_time = None
                            tile.grown = False
                        else:
                            selected_tile = tile
                            tab_active = True
                        break
            elif tab_active and selected_tile is not None:
                # Tab selection buttons
                if soil_tab_btn_rect.collidepoint(event.pos):
                    active_tab = "soil"
                if plants_tab_btn_rect.collidepoint(event.pos):
                    active_tab = "plants"
                if fertiliser_tab_btn_rect.collidepoint(event.pos):
                    active_tab = "fertiliser"
                # Check if close button is clicked
                close_size = 18
                close_rect = pygame.Rect(tab_rect.right - close_size - 8, tab_rect.y + 8, close_size, close_size)
                if close_rect.collidepoint(event.pos):
                    tab_active = False
                    selected_tile = None
                # Check if any option button is clicked
                if active_tab == "soil":
                    for idx in range(num_soils):
                        option_rect = pygame.Rect(
                            tab_rect.x + 8,
                            tab_rect.y + tab_button_height + 40 + idx * (option_height + option_spacing),
                            option_width,
                            option_height
                        )
                        if option_rect.collidepoint(event.pos):
                            selected_tile.soil = idx
                elif active_tab == "plants":
                    for idx in range(num_plants):
                        option_rect = pygame.Rect(
                            tab_rect.x + 8,
                            tab_rect.y + tab_button_height + 40 + idx * (option_height + option_spacing),
                            option_width,
                            option_height
                        )
                        if option_rect.collidepoint(event.pos):
                            selected_tile.plant = idx
                            selected_tile.plant_time = time.time()
                            selected_tile.grown = False
                elif active_tab == "fertiliser":
                    for idx in range(num_fertilisers):
                        option_rect = pygame.Rect(
                            tab_rect.x + 8,
                            tab_rect.y + tab_button_height + 40 + idx * (option_height + option_spacing),
                            option_width,
                            option_height
                        )
                        if option_rect.collidepoint(event.pos):
                            selected_tile.fertiliser = idx
    pygame.display.flip()

pygame.quit()