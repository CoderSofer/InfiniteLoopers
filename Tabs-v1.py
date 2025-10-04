import pygame

pygame.init()
screen = pygame.display.set_mode((700, 500))
pygame.display.set_caption("Farm Game")
#field cell
fieldCell_rect = pygame.Rect(150, 120, 50, 50)

#tabs
tab_active = False
tab_rect = pygame.Rect(fieldCell_rect.x + 30, fieldCell_rect.y - 60, 350, 100)
tab_font = pygame.font.SysFont(None, 18)

# Number of option buttons to display
num_soils = 5  # Change this value to set the number of buttons
option_labels = [f"Soil{i+1}" for i in range(num_soils)]

# Option button dimensions
option_height = 20
option_width = 100
option_spacing = 8

# Soil color mapping
soil_colors = [
    (139, 69, 19),   # Soil1 - brown
    (160, 82, 45),   # Soil2 - sienna
    (205, 133, 63),  # Soil3 - peru
    (222, 184, 135), # Soil4 - burlywood
    (244, 164, 96)   # Soil5 - sandy brown
]

# Track selected soil, plant and fertiliser

selected_soil = None
selected_plant = None
selected_fertiliser = None

# Fertiliser options and colors
num_fertilisers = 3
fertiliser_labels = [f"Fertiliser{i+1}" for i in range(num_fertilisers)]
fertiliser_colors = [
    (255, 215, 0),   # Fertiliser1 - gold
    (128, 128, 128), # Fertiliser2 - gray
    (255, 255, 255)  # Fertiliser3 - white
]

# Plant options and colors
num_plants = 4
plant_labels = [f"Plant{i+1}" for i in range(num_plants)]
plant_colors = [
    (34, 139, 34),   # Plant1 - green
    (60, 179, 113),  # Plant2 - medium sea green
    (107, 142, 35),  # Plant3 - olive drab
    (154, 205, 50)   # Plant4 - yellow green
]

# Tab selection state
active_tab = "soil"  # can be "soil", "plants", or "fertiliser"

# Calculate tab size dynamically
tab_width = 350
tab_height = 80 + num_soils * (option_height + option_spacing)
tab_rect = pygame.Rect(fieldCell_rect.x + 30, fieldCell_rect.y - 60, tab_width, tab_height)

running = True
while running:
    screen.fill((30, 30, 30))
    # Draw field cell fill based on soil selection
    if selected_soil is not None:
        pygame.draw.rect(screen, soil_colors[selected_soil], fieldCell_rect)
    else:
        pygame.draw.rect(screen, (70, 130, 180), fieldCell_rect)

    # Draw field cell outline based on plant selection (inner outline)
    if selected_plant is not None:
        pygame.draw.rect(screen, plant_colors[selected_plant], fieldCell_rect, 4)
    else:
        pygame.draw.rect(screen, (0, 0, 0), fieldCell_rect, 2)

    # Draw field cell outer outline based on fertiliser selection
    outer_rect = fieldCell_rect.inflate(8, 8)
    if selected_fertiliser is not None:
        pygame.draw.rect(screen, fertiliser_colors[selected_fertiliser], outer_rect, 4)
    else:
        pygame.draw.rect(screen, (0, 0, 0), outer_rect, 2)

    if tab_active:
        # Recalculate tab size for current tab
        if active_tab == "soil":
            tab_height = 80 + num_soils * (option_height + option_spacing)
        else:
            tab_height = 80 + num_plants * (option_height + option_spacing)
        tab_rect = pygame.Rect(fieldCell_rect.x + 30, fieldCell_rect.y - 60, tab_width, tab_height)

        # Draw tab background
        pygame.draw.rect(screen, (220, 220, 220), tab_rect)

        # Tab selection buttons
        tab_button_width = 60
        tab_button_height = 24
        soil_tab_btn_rect = pygame.Rect(tab_rect.x + 8, tab_rect.y + 8, tab_button_width, tab_button_height)
        plants_tab_btn_rect = pygame.Rect(tab_rect.x + 8 + tab_button_width + 8, tab_rect.y + 8, tab_button_width, tab_button_height)
        fertiliser_tab_btn_rect = pygame.Rect(tab_rect.x + 8 + 2 * (tab_button_width + 8), tab_rect.y + 8, tab_button_width, tab_button_height)
        pygame.draw.rect(screen, (180, 180, 180) if active_tab == "soil" else (220, 220, 220), soil_tab_btn_rect)
        pygame.draw.rect(screen, (180, 180, 180) if active_tab == "plants" else (220, 220, 220), plants_tab_btn_rect)
        pygame.draw.rect(screen, (180, 180, 180) if active_tab == "fertiliser" else (220, 220, 220), fertiliser_tab_btn_rect)
        pygame.draw.rect(screen, (0, 0, 0), soil_tab_btn_rect, 2)
        pygame.draw.rect(screen, (0, 0, 0), plants_tab_btn_rect, 2)
        pygame.draw.rect(screen, (0, 0, 0), fertiliser_tab_btn_rect, 2)
        soil_btn_text = tab_font.render("Soil", True, (0, 0, 0))
        plants_btn_text = tab_font.render("Plants", True, (0, 0, 0))
        fertiliser_btn_text = tab_font.render("Fertiliser", True, (0, 0, 0))
        screen.blit(soil_btn_text, (soil_tab_btn_rect.x + 8, soil_tab_btn_rect.y + 2))
        screen.blit(plants_btn_text, (plants_tab_btn_rect.x + 8, plants_tab_btn_rect.y + 2))
        screen.blit(fertiliser_btn_text, (fertiliser_tab_btn_rect.x + 2, fertiliser_tab_btn_rect.y + 2))

        # Draw a close button (top right corner)
        close_size = 18
        close_rect = pygame.Rect(tab_rect.right - close_size - 8, tab_rect.y + 8, close_size, close_size)
        pygame.draw.rect(screen, (200, 50, 50), close_rect)
        close_text = tab_font.render("X", True, (255, 255, 255))
        text_rect = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, text_rect)

        # Draw option buttons dynamically for active tab
        option_rects = []
        if active_tab == "soil":
            tab_text = tab_font.render("Choose your type of soil", True, (0, 0, 0))
            screen.blit(tab_text, (tab_rect.x + 8, tab_rect.y + tab_button_height + 16))
            for i, label in enumerate(option_labels):
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
            if not tab_active and fieldCell_rect.collidepoint(event.pos):
                tab_active = True
            elif tab_active:
                # Tab selection buttons
                tab_button_width = 60
                tab_button_height = 24
                soil_tab_btn_rect = pygame.Rect(tab_rect.x + 8, tab_rect.y + 8, tab_button_width, tab_button_height)
                plants_tab_btn_rect = pygame.Rect(tab_rect.x + 8 + tab_button_width + 8, tab_rect.y + 8, tab_button_width, tab_button_height)
                fertiliser_tab_btn_rect = pygame.Rect(tab_rect.x + 8 + 2 * (tab_button_width + 8), tab_rect.y + 8, tab_button_width, tab_button_height)
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
                            selected_soil = idx
                elif active_tab == "plants":
                    for idx in range(num_plants):
                        option_rect = pygame.Rect(
                            tab_rect.x + 8,
                            tab_rect.y + tab_button_height + 40 + idx * (option_height + option_spacing),
                            option_width,
                            option_height
                        )
                        if option_rect.collidepoint(event.pos):
                            selected_plant = idx
                elif active_tab == "fertiliser":
                    for idx in range(num_fertilisers):
                        option_rect = pygame.Rect(
                            tab_rect.x + 8,
                            tab_rect.y + tab_button_height + 40 + idx * (option_height + option_spacing),
                            option_width,
                            option_height
                        )
                        if option_rect.collidepoint(event.pos):
                            selected_fertiliser = idx

    pygame.display.flip()

pygame.quit()