import time
import pygame
from game import FieldScene
from game.store import ShopPopup 
from game.guidebook import BookScene
from game.sounds import SoundBank 

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

# Pass sfx into FieldScene 
field = FieldScene(screen.get_size(), fonts=fonts, sfx=sfx)
STATE = "HOME"
home_ui = {}
running = True

shop = ShopPopup(fonts={"tab": fonts["tab"], "title": fonts["title"]})
book = BookScene(screen) 

def draw_home(surf):
    surf.fill((30, 30, 30))
    title = fonts["home"].render("Farm Game — Home", True, (255, 255, 255))
    surf.blit(title, (20, 20))
    btn = pygame.Rect(300, 260, 200, 60)
    pygame.draw.rect(surf, (90, 90, 90), btn, border_radius=12)
    txt = fonts["home"].render("Enter Field", True, (255, 255, 255))
    surf.blit(txt, txt.get_rect(center=btn.center))
    return {"enter_btn": btn}

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
    else:
        home_ui = draw_home(screen)


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
                STATE = "HOME"
        elif STATE == "BOOK":
            # simple exit for now
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                STATE = "FIELD"
        else:  # HOME
            if event.type == pygame.MOUSEBUTTONDOWN and home_ui.get("enter_btn", pygame.Rect(0,0,0,0)).collidepoint(event.pos):
                STATE = "FIELD"

    pygame.display.flip()

pygame.quit()
