import time
import pygame
from game import FieldScene
from game.store import ShopPopup 
from game.guidebook import BookScene
from game.sounds import SoundBank 
from game.homePage import main_page

pygame.init()
pygame.mixer.init() 
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Farm Game")
clock = pygame.time.Clock()

# Load SFX
sfx = SoundBank(volume=0.9)
sfx.load() 

fonts = {
    "tab": pygame.font.SysFont(None, 24),
    "home": pygame.font.SysFont(None, 32),
    "title": pygame.font.SysFont(None, 22),  
}

shop = ShopPopup(fonts={"tab": fonts["tab"], "title": fonts["title"]})
field = FieldScene(screen.get_size(), fonts=fonts, shop=shop, sfx=sfx)
book = BookScene(screen) 

# Show your homepage first, then start FIELD if Play is clicked
action = main_page()
if action == "QUIT":
    pygame.quit()
    raise SystemExit
STATE = "FIELD"

running = True

# Pass sfx into FieldScene 
field = FieldScene(screen.get_size(), fonts=fonts, sfx=sfx)

shop = ShopPopup(fonts={"tab": fonts["tab"], "title": fonts["title"]})
book = BookScene(screen) 

# Show your homepage first, then start FIELD if Play is clicked
action = main_page()
if action == "QUIT":
    pygame.quit()
    raise SystemExit
STATE = "FIELD"

running = True

while running:
    dt = clock.tick(60) / 1000.0
    now = time.time()

    # draw first so FieldScene can cache UI rects for events
    if STATE == "FIELD":
        field.update(now)
        field.draw(screen)
        # If the Shop button is toggled on, draw the popup
        if getattr(field, "shop_open", False):
            grid_geom = {
                "start_x": field.start_x,
                "start_y": field.start_y,
                "cols": field.cfg["COLS"],
                "rows": field.cfg["ROWS"],
                "tile_size": field.cfg["TILE_SIZE"],
                "gap": field.cfg["GAP"],
            }
            shop.active = True  # ensure it's visible once toggled on
            shop.draw(screen, grid_geom)
    elif STATE == "BOOK":
        book.draw()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if STATE == "FIELD":
            # If shop is open, let the popup eat events first
            if getattr(field, "shop_open", False):
                grid_geom = {
                    "start_x": field.start_x,
                    "start_y": field.start_y,
                    "cols": field.cfg["COLS"],
                    "rows": field.cfg["ROWS"],
                    "tile_size": field.cfg["TILE_SIZE"],
                    "gap": field.cfg["GAP"],
                }
                if shop.handle_event(event, grid_geom):
                    # If it just closed, sync the toggle back to the scene
                    if not shop.active:
                        field.shop_open = False
                    continue  # popup consumed the event
                # transition to Guidebook if the field asked for it
            if getattr(field, "want_guidebook", False):
                field.want_guidebook = False
                STATE = "BOOK"
            # Otherwise, normal field input (this includes the Shop button toggle)
            field.handle_event(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # <<< NEW: go to your homepage; if they quit there, exit; if they hit Play, return to FIELD
                act = main_page()
                if act == "QUIT":
                    running = False
                else:
                    STATE = "FIELD"
                continue

        elif STATE == "BOOK":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                STATE = "FIELD"

    pygame.display.flip()

pygame.quit()
