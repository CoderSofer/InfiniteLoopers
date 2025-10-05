# game/field_logic.py
import time
import pygame
from typing import Tuple, Optional
import os

# ---- Config / data ----
SOIL_LABELS = ["Loose & well-draining", "Rich & well-draining", "Deep & Loose", "Loamy", "Well-draining"]


PLANT_LABELS = ["Carrots", "Potatoes", "Tomatoes", "Cucumbers", "Lentils"]
PLANT_COLORS = [(237,145,33), (255,251,149), (255,99,71), (103,171,5), (126,105,95)]

FERT_LABELS = ["Nitrogen", "Phosphorus", "potassium"]
FERT_COLORS = [(255,215,0), (128,128,128), (255,255,255)]

# Which soils are valid for each plant index
ALLOWED_SOILS = {
    0: [2],      # Carrots: Deep and Lose
    1: [0],      # Potatoes: Lose and well-draining
    2: [1],      # Tomatoes: Rich and well-draining
    3: [3],         # Cucumbers: Loamy
    4: [4]          # Lentils: Well-draining
}

DEFAULTS = {
    "ROWS": 3, "COLS": 3, "TILE_SIZE": 120, "GAP": 12,
    "TILE_COLOUR": (107, 66, 40),
    "BACKGROUND_COLOR": (245, 228, 156),
    "TAB_BTN": (78, 177, 78),
    "TAB_BTN_ACTIVE": (0, 118, 0),
}

SHOP_BTN_IDLE  = (78, 177, 78)
SHOP_BTN_HOVER = (0, 118, 0)
SHOP_BTN_TEXT  = (0, 0, 0)
SHOP_BTN_BORDER = (0, 0, 0)

# ---- Load soil images ----
SOIL_IMAGES = []
for i in range(5):
    img_path = os.path.join(os.path.dirname(__file__), f'..', f'soil{i+1}.png')
    img = pygame.image.load(img_path)
    img = pygame.transform.smoothscale(img, (DEFAULTS["TILE_SIZE"], DEFAULTS["TILE_SIZE"]))
    SOIL_IMAGES.append(img)

PLANT_IMAGES = []
for i in range(5):
    img_path = os.path.join(os.path.dirname(__file__), f'..', f'plant{i+1}.png')
    img = pygame.image.load(img_path)


    # p_size = (int(img.get_width() *0.8), int(img.get_height() *0.8))
    # img = pygame.transform.smoothscale(img, p_size)
    img = pygame.transform.smoothscale(img, (100,100))
    PLANT_IMAGES.append(img)


# ---- Shop button helpers ----
def make_shop_button_rect(start_x, start_y, cols, rows, tile_size, gap,
                          *, anchor="top-right", size=(96, 28), offset=(0, 8)) -> pygame.Rect:
    grid_w = cols * tile_size + (cols - 1) * gap
    grid_h = rows * tile_size + (rows - 1) * gap
    w, h = size
    if anchor == "top-left":
        x = start_x;                  y = start_y - h - offset[1]
    elif anchor == "bottom-left":
        x = start_x;                  y = start_y + grid_h + offset[1]
    elif anchor == "bottom-right":
        x = start_x + grid_w - w;     y = start_y + grid_h + offset[1]
    else:  # "top-right"
        x = start_x + grid_w - w;     y = start_y - h - offset[1]
    return pygame.Rect(x, y, w, h)

def draw_shop_button(surface, rect, font, hovered, label="Shop") -> None:
    bg = SHOP_BTN_HOVER if hovered else SHOP_BTN_IDLE
    pygame.draw.rect(surface, bg, rect, border_radius=6)
    pygame.draw.rect(surface, SHOP_BTN_BORDER, rect, width=2, border_radius=6)
    if font:
        txt = font.render(label, True, SHOP_BTN_TEXT)
        surface.blit(txt, txt.get_rect(center=rect.center))


def compute_grid_start(sw, sh, cols, rows, tile, gap):
    grid_w = cols * tile + (cols - 1) * gap
    grid_h = rows * tile + (rows - 1) * gap
    return (sw - grid_w) // 2, (sh - grid_h) // 2

class Tile:
    def __init__(self, row, col, start_x, start_y, tile_size, gap, shop=None):
        self.row, self.col = row, col
        x = start_x + col * (tile_size + gap)
        y = start_y + row * (tile_size + gap)
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.soil = None
        self.plant = None
        self.fertiliser = None
        self.plant_time = None
        self.grown = False
        self.shop = shop

    def update_growth(self, now):
        if self.plant is None or self.plant_time is None:
            self.grown = False
            return
        if self.soil in ALLOWED_SOILS.get(self.plant, set()):
            if not self.grown and (now - self.plant_time) >= 10:
                self.grown = True
        else:
            self.grown = False

    def draw(self, surf, tile_colour):
        # Draw soil image if chosen
        if self.soil is not None:
            img = SOIL_IMAGES[self.soil]
            mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255,255,255,255), mask.get_rect(), border_radius=12)
            rounded_img = img.copy()
            rounded_img.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(rounded_img, self.rect)
        else:
            pygame.draw.rect(surf, tile_colour, self.rect, border_radius=12)

        if self.plant is not None:
            pygame.draw.rect(surf, PLANT_COLORS[self.plant], self.rect, 4, border_radius=12)
            if self.grown:
                img = PLANT_IMAGES[self.plant]
                surf.blit(img, (self.rect.x + (self.rect.width - img.get_width()) // 2,
                                self.rect.y + (self.rect.height - img.get_height()) // 2))
        else:
            pygame.draw.rect(surf, (0, 0, 0), self.rect, 2, border_radius=12)

        outer = self.rect.inflate(8, 8)
        if self.fertiliser is not None:
            pygame.draw.rect(surf, FERT_COLORS[self.fertiliser], outer, 4, border_radius=16)
        else:
            pygame.draw.rect(surf, (0, 0, 0), outer, 2, border_radius=16)

class FieldScene:
    """
    Self-contained scene mounted in main.py

    Methods:
      - update(now)
      - draw(surface)
      - handle_event(event)
    """
    def __init__(self, screen_size, fonts=None, config=None, shop=None, sfx=None): 
        self.w, self.h = screen_size
        self.cfg = {**DEFAULTS, **(config or {})}
        self.font = (fonts or {}).get("tab", pygame.font.SysFont(None, 24))
        self.sfx = sfx

        self.start_x, self.start_y = compute_grid_start(
            self.w, self.h, self.cfg["COLS"], self.cfg["ROWS"], self.cfg["TILE_SIZE"], self.cfg["GAP"]
        )

        self.shop = shop
        self.tiles = [
            Tile(r, c, self.start_x, self.start_y, self.cfg["TILE_SIZE"], self.cfg["GAP"], shop=self.shop)
            for r in range(self.cfg["ROWS"]) for c in range(self.cfg["COLS"])
        ]

        self.selected = None
        self.tab_active = False
        self.active_tab = "soil"  # "soil" | "plants" | "fertiliser"
        self.ui = {}  # cache of rects from last draw

        self.shop_open = False
        self.shop_button_rect = make_shop_button_rect(
            self.start_x, self.start_y,
            self.cfg["COLS"], self.cfg["ROWS"],
            self.cfg["TILE_SIZE"], self.cfg["GAP"],
            anchor="top-right", size=(96, 28), offset=(0, 8)
        )
        # --- Guidebook button placed just left of the Shop button ---
        self.want_guidebook = False
        _bw, _bh = self.shop_button_rect.size
        self.guide_button_rect = pygame.Rect(
            self.shop_button_rect.x - _bw - 8,  # 8px gap to the left of Shop
            self.shop_button_rect.y,
            _bw, _bh
        )


    def update(self, now=None):
        now = now or time.time()
        for t in self.tiles:
            t.update_growth(now)

    def draw(self, surface):
        surface.fill(self.cfg["BACKGROUND_COLOR"])
        for t in self.tiles:
            t.draw(surface, self.cfg["TILE_COLOUR"])

        self.ui.clear()
        if self.tab_active and self.selected:
            self._draw_tab(surface)

        # Shop button on/above the grid
        hovered = self.shop_button_rect.collidepoint(pygame.mouse.get_pos())
        draw_shop_button(surface, self.shop_button_rect, self.font, hovered, label="Shop")


        # Guidebook button
        hovered_g = self.guide_button_rect.collidepoint(pygame.mouse.get_pos())
        draw_shop_button(surface, self.guide_button_rect, self.font, hovered_g, label="Guide")


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.shop_button_rect.collidepoint(pos):
                self.shop_open = not self.shop_open
                if self.sfx: self.sfx.play("CLICK")
                return
            if self.guide_button_rect.collidepoint(pos):
                self.want_guidebook = True
                if self.sfx: self.sfx.play("CLICK")
                return
            if not self.tab_active:
                for t in self.tiles:
                    if t.rect.collidepoint(pos):
                        if self.sfx: self.sfx.play("CLICK")
                        # harvest if grown
                        if t.plant is not None and t.grown:
                            # Add harvested crop to inventory
                            if self.shop:
                                crop_names = ["Carrot", "Potato", "Tomato", "Cucumber", "Lentils"]
                                crop_name = crop_names[t.plant]
                                self.shop._add_to_inventory(self.shop.inv_crops, crop_name, 1)
                            t.plant = None
                            t.plant_time = None
                            t.grown = False
                        else:
                            self.selected = t
                            self.tab_active = True
                        break
            else:
                # switch tabs
                if self.ui.get("soil_btn") and self.ui["soil_btn"].collidepoint(pos):
                    if self.sfx: self.sfx.play("CLICK")
                    self.active_tab = "soil"
                if self.ui.get("plant_btn") and self.ui["plant_btn"].collidepoint(pos):
                    if self.sfx: self.sfx.play("CLICK")
                    self.active_tab = "plants"
                if self.ui.get("fert_btn") and self.ui["fert_btn"].collidepoint(pos):
                    if self.sfx: self.sfx.play("CLICK")
                    self.active_tab = "fertiliser"

                # close
                if self.ui.get("close_btn") and self.ui["close_btn"].collidepoint(pos):
                    if self.sfx: self.sfx.play("CLICK")
                    self.tab_active = False
                    self.selected = None
                    return

                # options
                opt_key = f"{self.active_tab}_options"
                for idx, rect in enumerate(self.ui.get(opt_key, [])):
                    if rect.collidepoint(pos):
                        if self.active_tab == "soil":
                            self.selected.soil = idx
                            if self.sfx: self.sfx.play("PICK")
                        elif self.active_tab == "plants":
                            # Only allow planting if you own the seed
                            if self.shop:
                                seed_names = ["Carrot Seeds", "Potato Seeds", "Tomato Seeds", "Cucumber Seeds", "Lentil Seeds"]
                                seed_name = seed_names[idx]
                                qty = self.shop._owned_qty(self.shop.inv_seeds, seed_name)
                                if qty > 0:
                                    # If a seed is already planted, return it to inventory
                                    prev_plant = self.selected.plant
                                    if prev_plant is not None:
                                        prev_seed_name = seed_names[prev_plant]
                                        self.shop._add_to_inventory(self.shop.inv_seeds, prev_seed_name, 1)
                                    self.selected.plant = idx
                                    if self.sfx: self.sfx.play("PICK")
                                    self.selected.plant_time = time.time()
                                    self.selected.grown = False
                                    self.shop._add_to_inventory(self.shop.inv_seeds, seed_name, -1)
                        elif self.active_tab == "fertiliser":
                            self.selected.fertiliser = idx
                            if self.sfx: self.sfx.play("PICK")


    # ---------- helpers ----------
    def _draw_tab(self, surf):
        tab_w, btn_w, btn_h = 300, 80, 30
        opt_h, opt_w, opt_gap = 20, 200, 3

        counts = {
            "soil": len(SOIL_LABELS),
            "plants": len(PLANT_LABELS),
            "fertiliser": len(FERT_LABELS),
        }
        tab_h = 120 + counts[self.active_tab] * (opt_h + opt_gap)

        # place to right unless it would overflow
        sel = self.selected
        if sel.rect.right + 20 + tab_w > self.w:
            tab_x = sel.rect.left - 20 - tab_w
        else:
            tab_x = sel.rect.right + 20
        tab_y = sel.rect.top

        tab_rect = pygame.Rect(tab_x, tab_y, tab_w, tab_h)
        pygame.draw.rect(surf, (255, 255, 255), tab_rect, border_radius=8)

        soil_r = pygame.Rect(tab_rect.x + 8, tab_rect.y + 8, btn_w, btn_h)
        plant_r = pygame.Rect(tab_rect.x + 8 + btn_w + 8, tab_rect.y + 8, btn_w, btn_h)
        fert_r = pygame.Rect(tab_rect.x + 8 + 2 * (btn_w + 8), tab_rect.y + 8, btn_w, btn_h)

        pygame.draw.rect(surf, self.cfg["TAB_BTN_ACTIVE"] if self.active_tab == "soil" else self.cfg["TAB_BTN"], soil_r, border_radius=4)
        pygame.draw.rect(surf, self.cfg["TAB_BTN_ACTIVE"] if self.active_tab == "plants" else self.cfg["TAB_BTN"], plant_r, border_radius=4)
        pygame.draw.rect(surf, self.cfg["TAB_BTN_ACTIVE"] if self.active_tab == "fertiliser" else self.cfg["TAB_BTN"], fert_r, border_radius=4)

        soil_txt = self.font.render("Soil", True, (255, 255, 255))
        plant_txt = self.font.render("Crops", True, (255, 255, 255))
        fert_txt = self.font.render("Fertiliser", True, (255, 255, 255))
        surf.blit(soil_txt, soil_txt.get_rect(center=soil_r.center))
        surf.blit(plant_txt, plant_txt.get_rect(center=plant_r.center))
        surf.blit(fert_txt, fert_txt.get_rect(center=fert_r.center))

        close_size = 18
        close_r = pygame.Rect(tab_rect.right - close_size - 8, tab_rect.y + 8, close_size, close_size)
        pygame.draw.rect(surf, (194, 43, 43), close_r, border_radius=4)
        x_txt = self.font.render("x", True, (255, 255, 255))
        surf.blit(x_txt, x_txt.get_rect(center=close_r.center))

        title_map = {
            "soil": "Choose your type of soil",
            "plants": "Choose your type of plant",
            "fertiliser": "Choose your fertiliser",
        }
        title = self.font.render(title_map[self.active_tab], True, (0, 0, 0))
        surf.blit(title, (tab_rect.x + 8, tab_rect.y + btn_h + 16))

        labels_map = {"soil": SOIL_LABELS, "plants": PLANT_LABELS, "fertiliser": FERT_LABELS}
        rects = []
        # Only show plant options for seeds you own
        owned_seeds = set()
        if self.active_tab == "plants" and self.shop:
            for seed in self.shop.inv_seeds:
                if seed.get("qty", 0) > 0:
                    # Map seed name to plant index
                    if "Carrot" in seed["name"]: owned_seeds.add(0)
                    if "Potato" in seed["name"]: owned_seeds.add(1)
                    if "Tomato" in seed["name"]: owned_seeds.add(2)
                    if "Cucumber" in seed["name"]: owned_seeds.add(3)
                    if "Lentil" in seed["name"]: owned_seeds.add(4)
        for i, label in enumerate(labels_map[self.active_tab]):
            r = pygame.Rect(
                tab_rect.x + 8,
                tab_rect.y + btn_h + 40 + i * (opt_h + opt_gap),
                opt_w,
                opt_h,
            )
            rects.append(r)
            if self.active_tab == "plants" and i not in owned_seeds:
                fill = (180, 180, 180)  # gray out if not owned
            else:
                fill = (100, 200, 100) if self.active_tab != "fertiliser" else (200, 200, 100)
            pygame.draw.rect(surf, fill, r)
            pygame.draw.rect(surf, (0, 0, 0), r, 2)
            text = self.font.render(label, True, (0, 0, 0))
            surf.blit(text, (r.x + 2, r.y + 2))

        # cache rects for event handling
        self.ui.update({
            "tab_rect": tab_rect,
            "soil_btn": soil_r,
            "plant_btn": plant_r,
            "fert_btn": fert_r,
            "close_btn": close_r,
            f"{self.active_tab}_options": rects,
        })
