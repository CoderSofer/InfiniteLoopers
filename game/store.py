# game/shop_popup.py
from __future__ import annotations
import pygame
from typing import Optional, Dict, Tuple

# ---- Colors / layout (safe at import) ----
COL_PANEL_BG = (220, 220, 220)
COL_PANEL_BORDER = (0, 0, 0)
COL_BTN = (190, 190, 190)
COL_BTN_ACTIVE = (160, 160, 160)
COL_GOOD = (100, 200, 100)
COL_BAD = (200, 80, 80)
COL_TEXT = (0, 0, 0)
COL_DISABLED = (180, 180, 180)
COL_SCROLL_TRACK = (210, 210, 210)
COL_SCROLL_THUMB = (150, 150, 150)

# Layout knobs
OPTION_H = 22
OPTION_SPACING = 6
TAB_WIDTH = 400
TAB_HEADER_H = 72       # title + top tabs row
SUBTAB_H = 28           # subtab row height (Buy/Inventory)
PANEL_HEIGHT = 320      # fixed height, scroll inside
CONTENT_PAD = 8
SCROLL_STEP = 40

def clamp(v, lo, hi): 
    return max(lo, min(hi, v))


class ShopPopup:
    """
    Self-contained Shop overlay (tabs, subtabs, scroll) with NO pygame.init at import time.
    Call:
      - shop = ShopPopup(fonts={'tab': tab_font, 'title': title_font})
      - if open toggle from your FieldScene button: shop.draw(screen, grid_geom)
      - route events to shop.handle_event(event, grid_geom)

    grid_geom = dict(
       start_x=..., start_y=..., cols=..., rows=..., tile_size=..., gap=...
    )
    """

    def __init__(self, fonts: Dict[str, pygame.font.Font], *, money: int = 200):
        # fonts: expect keys 'tab' and 'title'
        self.font_tab = fonts.get('tab')
        self.font_title = fonts.get('title', self.font_tab)

        # ---- Game state (you can replace with your own) ----
        self.money = money

        # SELL: crops & prices
        self.crops = {"Wheat": 3, "Corn": 2, "Potato": 0, "Strawberry": 5}
        self.sell_prices = {"Wheat": 8, "Corn": 12, "Potato": 6, "Strawberry": 20}

        # BUY: sections
        self.shop_seeds = [
            {"name": "Wheat Seeds", "price": 4},
            {"name": "Corn Seeds", "price": 6},
            {"name": "Potato Seeds", "price": 5},
            {"name": "Strawberry Seeds", "price": 12},
            {"name": "Pumpkin Seeds", "price": 15},
        ]
        self.shop_dirt = [
            {"name": "Loam", "price": 15},
            {"name": "Sandy", "price": 10},
            {"name": "Clay", "price": 18},
            {"name": "Compost Soil", "price": 22},
        ]
        self.shop_ferts = [
            {"name": "Fertiliser A", "price": 25},
            {"name": "Fertiliser B", "price": 35},
            {"name": "Fertiliser C", "price": 50},
        ]
        self.shop_tools = [
            {"name": "Hoe", "price": 40, "color": (255,170,80)},
            {"name": "Watering Can", "price": 60, "color": (120,200,255)},
            {"name": "Scythe", "price": 85, "color": (200,200,200)},
            {"name": "Axe", "price": 75, "color": (240,120,120)},
        ]

        # INVENTORY mirrors
        self.inv_seeds = {"Wheat Seeds": 0, "Corn Seeds": 0, "Potato Seeds": 0, "Strawberry Seeds": 0}
        self.inv_dirt  = {"Loam": 0, "Sandy": 0, "Clay": 0, "Compost Soil": 0}
        self.inv_ferts = {"Fertiliser A": 0, "Fertiliser B": 0, "Fertiliser C": 0}
        self.tools_owned = []  # list of {"name","color"}
        self.equipped_tool: Optional[int] = None

        # ---- UI state ----
        self.active = True                 # the popup is visible when True
        self.active_tab = "buy"            # "buy" | "sell" | "inventory"
        self.buy_subtab = "seeds"          # "seeds" | "dirt" | "ferts" | "tools"
        self.inv_subtab = "seeds"          # "seeds" | "dirt" | "ferts" | "tools" | "crops"

        # scroll offsets per-(tab,subtab)
        self.scroll = {
            "buy:seeds": 0, "buy:dirt": 0, "buy:ferts": 0, "buy:tools": 0,
            "sell": 0,
            "inv:seeds": 0, "inv:dirt": 0, "inv:ferts": 0, "inv:tools": 0, "inv:crops": 0,
        }
        # drag state
        self.scroll_dragging = False
        self.drag_key = None
        self.drag_anchor_y = 0
        self.drag_anchor_scroll = 0

    # ----------------- geometry helpers -----------------
    def _grid_rect(self, g: Dict) -> pygame.Rect:
        """Rectangle that bounds the grid area (for anchoring the popup)."""
        grid_w = g["cols"] * g["tile_size"] + (g["cols"] - 1) * g["gap"]
        grid_h = g["rows"] * g["tile_size"] + (g["rows"] - 1) * g["gap"]
        return pygame.Rect(g["start_x"], g["start_y"], grid_w, grid_h)

    # replace your existing _shop_rect with this version
    def _shop_rect(self, g: Dict, sw: int, sh: int) -> pygame.Rect:
        grid_w = g["cols"] * g["tile_size"] + (g["cols"] - 1) * g["gap"]
        grid_h = g["rows"] * g["tile_size"] + (g["rows"] - 1) * g["gap"]
        grid_r = pygame.Rect(g["start_x"], g["start_y"], grid_w, grid_h)

        # keep the panel within the window
        w = min(TAB_WIDTH, max(200, sw - 16))   # never wider than screen
        h = min(PANEL_HEIGHT, max(160, sh - 16))

        # prefer right of the grid
        x = grid_r.right + 16
        y = grid_r.top

        # if it doesn't fit on the right, try left of the grid
        if x + w > sw:
            alt_x = grid_r.left - 16 - w
            x = alt_x if alt_x >= 0 else max(0, sw - w)

        # clamp vertically
        if y + h > sh:
            y = max(0, sh - h)

        return pygame.Rect(x, y, w, h)


    def _content_clip(self, shop_rect: pygame.Rect, include_subtabs: bool) -> pygame.Rect:
        top = shop_rect.y + TAB_HEADER_H + (SUBTAB_H + 8 if include_subtabs else 0)
        return pygame.Rect(
            shop_rect.x + CONTENT_PAD, top,
            TAB_WIDTH - 2 * CONTENT_PAD - 10,     # 10px for scrollbar
            PANEL_HEIGHT - (top - shop_rect.y) - CONTENT_PAD
        )

    def _calc_content_height(self, key: str) -> int:
        def rows(n): return n * (OPTION_H + OPTION_SPACING)
        if key == "sell":
            return rows(len(self.crops))
        ktab, ksub = (key.split(":") + [""])[:2]
        if ktab == "buy":
            if ksub == "seeds": return rows(len(self.shop_seeds))
            if ksub == "dirt":  return rows(len(self.shop_dirt))
            if ksub == "ferts": return rows(len(self.shop_ferts))
            if ksub == "tools": return rows(len(self.shop_tools))
        if ktab == "inv":
            if ksub == "seeds": return rows(len(self.inv_seeds))
            if ksub == "dirt":  return rows(len(self.inv_dirt))
            if ksub == "ferts": return rows(len(self.inv_ferts))
            if ksub == "tools": return rows(len(self.tools_owned))
            if ksub == "crops": return rows(len(self.crops))
        return 0

    # ----------------- drawing primitives -----------------
    def _draw_tab_button(self, surface, rect, label, active):
        pygame.draw.rect(surface, COL_BTN_ACTIVE if active else COL_BTN, rect)
        pygame.draw.rect(surface, COL_PANEL_BORDER, rect, 2)
        lbl = self.font_tab.render(label, True, COL_TEXT)
        surface.blit(lbl, (rect.x + 6, rect.y + 4))

    def _draw_subtabs(self, surface, shop_rect, current, y, include_crops=False):
        labels = [("seeds", "Seeds"), ("dirt", "Dirt"), ("ferts", "Fertilisers"), ("tools", "Tools")]
        if include_crops:
            labels.append(("crops", "Crops"))
        rects = {}
        x = shop_rect.x + 8
        w = 84
        for key, label in labels:
            r = pygame.Rect(x, y, w, 24)
            self._draw_tab_button(surface, r, label, current == key)
            rects[key] = r
            x += w + 6
        return rects

    def _draw_scrollbar(self, surface, key, content_clip, content_h):
        if content_h <= content_clip.h:
            return None
        track = pygame.Rect(content_clip.right + 2, content_clip.y, 8, content_clip.h)
        pygame.draw.rect(surface, COL_SCROLL_TRACK, track)
        ratio = content_clip.h / max(1, content_h)
        thumb_h = max(24, int(track.h * ratio))
        max_scroll = max(0, content_h - content_clip.h)
        pos_ratio = 0 if max_scroll == 0 else (self.scroll[key] / max_scroll)
        thumb_y = track.y + int((track.h - thumb_h) * pos_ratio)
        thumb = pygame.Rect(track.x, thumb_y, track.w, thumb_h)
        pygame.draw.rect(surface, COL_SCROLL_THUMB, thumb)
        pygame.draw.rect(surface, COL_PANEL_BORDER, track, 1)
        pygame.draw.rect(surface, COL_PANEL_BORDER, thumb, 1)
        return track, thumb, max_scroll

    # ----------------- PUBLIC: draw + events -----------------
    def draw(self, surface: pygame.Surface, grid_geom: Dict) -> None:
        """Render the entire popup shop."""
        if not self.active:
            return

        sw, sh = surface.get_size()
        shop_rect = self._shop_rect(grid_geom, sw, sh)

        # Panel
        pygame.draw.rect(surface, COL_PANEL_BG, shop_rect)
        pygame.draw.rect(surface, COL_PANEL_BORDER, shop_rect, 2)

        # Header (title + money + close)
        title_text = self.font_title.render("Farm Shop", True, COL_TEXT)
        surface.blit(title_text, (shop_rect.x + 8, shop_rect.y + 8))

        close_size = 18
        close_rect = pygame.Rect(shop_rect.right - close_size - 8, shop_rect.y + 8, close_size, close_size)
        pygame.draw.rect(surface, COL_BAD, close_rect)
        x_txt = self.font_tab.render("X", True, (255, 255, 255))
        surface.blit(x_txt, x_txt.get_rect(center=close_rect.center))

        money_text = self.font_title.render(f"${self.money}", True, COL_TEXT)
        money_x = close_rect.x - 8 - money_text.get_width()
        money_y = shop_rect.y + 8
        surface.blit(money_text, (money_x, money_y))

        # Tabs
        tab_w, tab_h = 70, 24
        tab_y = shop_rect.y + 34
        buy_tab_rect  = pygame.Rect(shop_rect.x + 8, tab_y, tab_w, tab_h)
        sell_tab_rect = pygame.Rect(buy_tab_rect.right + 8, tab_y, tab_w, tab_h)
        inv_tab_rect  = pygame.Rect(sell_tab_rect.right + 8, tab_y, tab_w + 30, tab_h)

        self._draw_tab_button(surface, buy_tab_rect, "Buy", self.active_tab == "buy")
        self._draw_tab_button(surface, sell_tab_rect, "Sell", self.active_tab == "sell")
        self._draw_tab_button(surface, inv_tab_rect,  "Inventory", self.active_tab == "inventory")

        # Content area
        if self.active_tab in ("buy", "inventory"):
            subtab_y = shop_rect.y + 34 + tab_h + 6
            current = self.buy_subtab if self.active_tab == "buy" else self.inv_subtab
            _ = self._draw_subtabs(surface, shop_rect, current, subtab_y, include_crops=(self.active_tab == "inventory"))
            content_clip = self._content_clip(shop_rect, include_subtabs=True)
            current_key = f"{'buy' if self.active_tab=='buy' else 'inv'}:{current}"
        else:
            content_clip = self._content_clip(shop_rect, include_subtabs=False)
            current_key = "sell"

        pygame.draw.rect(surface, (235, 235, 235), content_clip)
        pygame.draw.rect(surface, COL_PANEL_BORDER, content_clip, 1)
        content_surf = surface.subsurface(content_clip)
        
        if content_clip.w <= 0 or content_clip.h <= 0:
            return

        # Render list items (with scroll)
        y_cursor = -self.scroll[current_key]

        if current_key.startswith("buy:"):
            sect = current_key.split(":")[1]
            if sect == "seeds":
                data = self.shop_seeds
                for item in data:
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(item["name"], True, COL_TEXT), (row.x + 6, row.y + 2))
                        content_surf.blit(self.font_tab.render(f"${item['price']}", True, COL_TEXT), (row.x + 160, row.y + 2))
                        btn = pygame.Rect(row.right - 60, row.y + 2, 56, row.h - 4)
                        pygame.draw.rect(content_surf, COL_GOOD if self.money >= item["price"] else COL_DISABLED, btn); pygame.draw.rect(content_surf, COL_PANEL_BORDER, btn, 1)
                        content_surf.blit(self.font_tab.render("Buy", True, COL_TEXT), (btn.x + 12, btn.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "dirt":
                data = self.shop_dirt
                for item in data:
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(item["name"], True, COL_TEXT), (row.x + 6, row.y + 2))
                        content_surf.blit(self.font_tab.render(f"${item['price']}", True, COL_TEXT), (row.x + 160, row.y + 2))
                        btn = pygame.Rect(row.right - 60, row.y + 2, 56, row.h - 4)
                        pygame.draw.rect(content_surf, COL_GOOD if self.money >= item["price"] else COL_DISABLED, btn); pygame.draw.rect(content_surf, COL_PANEL_BORDER, btn, 1)
                        content_surf.blit(self.font_tab.render("Buy", True, COL_TEXT), (btn.x + 12, btn.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "ferts":
                data = self.shop_ferts
                for item in data:
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(item["name"], True, COL_TEXT), (row.x + 6, row.y + 2))
                        content_surf.blit(self.font_tab.render(f"${item['price']}", True, COL_TEXT), (row.x + 160, row.y + 2))
                        btn = pygame.Rect(row.right - 60, row.y + 2, 56, row.h - 4)
                        pygame.draw.rect(content_surf, COL_GOOD if self.money >= item["price"] else COL_DISABLED, btn); pygame.draw.rect(content_surf, COL_PANEL_BORDER, btn, 1)
                        content_surf.blit(self.font_tab.render("Buy", True, COL_TEXT), (btn.x + 12, btn.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "tools":
                data = self.shop_tools
                for tool in data:
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        icon = pygame.Rect(row.x + 6, row.y + 3, 16, 16)
                        pygame.draw.rect(content_surf, tool["color"], icon)
                        content_surf.blit(self.font_tab.render(tool["name"], True, COL_TEXT), (icon.right + 6, row.y + 2))
                        content_surf.blit(self.font_tab.render(f"${tool['price']}", True, COL_TEXT), (row.x + 200, row.y + 2))
                        btn = pygame.Rect(row.right - 70, row.y + 2, 66, row.h - 4)
                        pygame.draw.rect(content_surf, COL_GOOD if self.money >= tool["price"] else COL_DISABLED, btn); pygame.draw.rect(content_surf, COL_PANEL_BORDER, btn, 1)
                        content_surf.blit(self.font_tab.render("Buy Tool", True, COL_TEXT), (btn.x + 4, btn.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

        elif current_key == "sell":
            for crop_name, qty in self.crops.items():
                row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                if row.bottom >= 0 and row.top <= content_clip.h:
                    pygame.draw.rect(content_surf, (240,240,240), row)
                    pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)

                    # reserve space for buttons right side
                    BTN_W, BTN_H, GAP, PAD = 58, row.h - 4, 6, 6
                    block_w = BTN_W + GAP + BTN_W + PAD
                    text_right = row.right - block_w

                    price_val = self.sell_prices.get(crop_name, 1)
                    name_s = self.font_tab.render(crop_name, True, COL_TEXT)
                    qty_s  = self.font_tab.render(f"x{qty}", True, COL_TEXT)
                    price_s= self.font_tab.render(f"${price_val} ea", True, COL_TEXT)

                    name_x  = row.x + 6
                    qty_x   = name_x + 160
                    price_x = text_right - price_s.get_width() - 6

                    content_surf.blit(name_s,  (name_x, row.y + 2))
                    content_surf.blit(qty_s,   (qty_x,  row.y + 2))
                    content_surf.blit(price_s, (price_x,row.y + 2))

                    can_sell = qty > 0
                    sell1  = pygame.Rect(text_right + PAD,   row.y + 2, BTN_W, BTN_H)
                    sellall= pygame.Rect(sell1.right + GAP,  row.y + 2, BTN_W, BTN_H)
                    for r, label in ((sell1,"Sell1"), (sellall,"All")):
                        pygame.draw.rect(content_surf, COL_BTN if can_sell else COL_DISABLED, r)
                        pygame.draw.rect(content_surf, COL_PANEL_BORDER, r, 1)
                        content_surf.blit(self.font_tab.render(label, True, COL_TEXT), (r.x + 8, r.y + 2))
                y_cursor += OPTION_H + OPTION_SPACING

        else:
            # Inventory subtabs
            sect = current_key.split(":")[1]
            if sect == "seeds":
                items = self.inv_seeds
                for name, qty in items.items():
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(name, True, COL_TEXT), (row.x + 6, row.y + 2))
                        content_surf.blit(self.font_tab.render(f"x{qty}", True, COL_TEXT), (row.x + 200, row.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "crops":
                for name, qty in self.crops.items():
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row)
                        pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(name, True, COL_TEXT), (row.x + 6, row.y + 2))
                        qty_lbl = self.font_tab.render(f"x{qty}", True, COL_TEXT)
                        content_surf.blit(qty_lbl, (row.right - qty_lbl.get_width() - 6, row.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "dirt":
                items = self.inv_dirt
                for name, qty in items.items():
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(name, True, COL_TEXT), (row.x + 6, row.y + 2))
                        content_surf.blit(self.font_tab.render(f"x{qty}", True, COL_TEXT), (row.x + 200, row.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "ferts":
                items = self.inv_ferts
                for name, qty in items.items():
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(name, True, COL_TEXT), (row.x + 6, row.y + 2))
                        content_surf.blit(self.font_tab.render(f"x{qty}", True, COL_TEXT), (row.x + 200, row.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "tools":
                for i, t in enumerate(self.tools_owned):
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        icon = pygame.Rect(row.x + 6, row.y + 3, 16, 16)
                        pygame.draw.rect(content_surf, t["color"], icon)
                        content_surf.blit(self.font_tab.render(t["name"], True, COL_TEXT), (icon.right + 6, row.y + 2))
                        is_eq = (self.equipped_tool == i)
                        btn = pygame.Rect(row.right - 80, row.y + 2, 76, row.h - 4)
                        pygame.draw.rect(content_surf, COL_BTN_ACTIVE if is_eq else COL_BTN, btn); pygame.draw.rect(content_surf, COL_PANEL_BORDER, btn, 1)
                        content_surf.blit(self.font_tab.render("Equipped" if is_eq else "Equip", True, COL_TEXT), (btn.x + 6, btn.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

        # Scrollbar
        content_h = self._calc_content_height(current_key)
        _ = self._draw_scrollbar(surface, current_key, content_clip, content_h)

        # Cache hit rects needed for events (recompute logic in handle_event)
        # We recompute in handle_event to stay in sync with drawing math.

    def handle_event(self, event: pygame.event.Event, grid_geom: Dict, sw: int = None, sh: int = None) -> bool:
        """
        Returns True if the event was consumed by the popup.
        Also updates `self.active` (False when closed).

        sw, sh: optional screen width/height. If not provided they are read from pygame.display.
        """
        if not self.active:
            return False

        # derive screen size if caller didn't supply it
        if sw is None or sh is None:
            surf = pygame.display.get_surface()
            if surf:
                sw, sh = surf.get_size()
            else:
                # fallback defaults
                sw, sh = 800, 600

        shop_rect = self._shop_rect(grid_geom, sw, sh)
        include_sub = (self.active_tab in ("buy", "inventory"))
        content_clip = self._content_clip(shop_rect, include_subtabs=include_sub)

        # -- close button area always clickable
        close_size = 18
        close_rect = pygame.Rect(shop_rect.right - close_size - 8, shop_rect.y + 8, close_size, close_size)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if close_rect.collidepoint(event.pos):
                self.active = False
                # stop scrolling drag whenever we close
                self.scroll_dragging = False
                self.drag_key = None
                return True

            # Tabs
            tab_w, tab_h = 70, 24
            tab_y = shop_rect.y + 34
            buy_tab_rect  = pygame.Rect(shop_rect.x + 8, tab_y, tab_w, tab_h)
            sell_tab_rect = pygame.Rect(buy_tab_rect.right + 8, tab_y, tab_w, tab_h)
            inv_tab_rect  = pygame.Rect(sell_tab_rect.right + 8, tab_y, tab_w + 30, tab_h)

            if buy_tab_rect.collidepoint(event.pos):
                self.active_tab = "buy"; return True
            if sell_tab_rect.collidepoint(event.pos):
                self.active_tab = "sell"; return True
            if inv_tab_rect.collidepoint(event.pos):
                self.active_tab = "inventory"; return True

            # Subtabs (for buy/inventory)
            if include_sub:
                sub_y = shop_rect.y + 34 + tab_h + 6
                # Recreate subtab rects same as draw
                labels = [("seeds","Seeds"), ("dirt","Dirt"), ("ferts","Fertilisers"), ("tools","Tools")]
                if self.active_tab == "inventory":
                    labels.append(("crops","Crops"))
                x = shop_rect.x + 8
                w = 84
                for key, _label in labels:
                    r = pygame.Rect(x, sub_y, w, 24)
                    if r.collidepoint(event.pos):
                        if self.active_tab == "buy": self.buy_subtab = key
                        else: self.inv_subtab = key
                        return True
                    x += w + 6

            # Scrollbar drag start?
            current_key = "sell" if self.active_tab=="sell" else (f"buy:{self.buy_subtab}" if self.active_tab=="buy" else f"inv:{self.inv_subtab}")
            content_h = self._calc_content_height(current_key)
            if content_h > content_clip.h:
                track = pygame.Rect(content_clip.right + 2, content_clip.y, 8, content_clip.h)
                ratio = content_clip.h / max(1, content_h)
                thumb_h = max(24, int(track.h * ratio))
                max_scroll = max(0, content_h - content_clip.h)
                pos_ratio = 0 if max_scroll == 0 else (self.scroll[current_key] / max_scroll)
                thumb_y = track.y + int((track.h - thumb_h) * pos_ratio)
                thumb = pygame.Rect(track.x, thumb_y, track.w, thumb_h)
                if thumb.collidepoint(event.pos):
                    self.scroll_dragging = True
                    self.drag_key = current_key
                    self.drag_anchor_y = event.pos[1]
                    self.drag_anchor_scroll = self.scroll[current_key]
                    return True

            # Content clicks
            if content_clip.collidepoint(event.pos):
                local_x = event.pos[0] - content_clip.x
                local_y = event.pos[1] - content_clip.y + self.scroll[current_key]
                y_cursor = 0

                if current_key.startswith("buy:"):
                    sect = current_key.split(":")[1]
                    if sect == "seeds":
                        for item in self.shop_seeds:
                            row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                            btn = pygame.Rect(row.right - 60, row.y + 2, 56, row.h - 4)
                            if btn.collidepoint((local_x, local_y)) and self.money >= item["price"]:
                                self.money -= item["price"]; self.inv_seeds[item["name"]] += 1
                                return True
                            y_cursor += OPTION_H + OPTION_SPACING
                    elif sect == "dirt":
                        for item in self.shop_dirt:
                            row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                            btn = pygame.Rect(row.right - 60, row.y + 2, 56, row.h - 4)
                            if btn.collidepoint((local_x, local_y)) and self.money >= item["price"]:
                                self.money -= item["price"]; self.inv_dirt[item["name"]] += 1
                                return True
                            y_cursor += OPTION_H + OPTION_SPACING
                    elif sect == "ferts":
                        for item in self.shop_ferts:
                            row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                            btn = pygame.Rect(row.right - 60, row.y + 2, 56, row.h - 4)
                            if btn.collidepoint((local_x, local_y)) and self.money >= item["price"]:
                                self.money -= item["price"]; self.inv_ferts[item["name"]] += 1
                                return True
                            y_cursor += OPTION_H + OPTION_SPACING
                    elif sect == "tools":
                        for tool in self.shop_tools:
                            row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                            btn = pygame.Rect(row.right - 70, row.y + 2, 66, row.h - 4)
                            if btn.collidepoint((local_x, local_y)) and self.money >= tool["price"]:
                                self.money -= tool["price"]; self.tools_owned.append({"name": tool["name"], "color": tool["color"]})
                                if self.equipped_tool is None: self.equipped_tool = 0
                                return True
                            y_cursor += OPTION_H + OPTION_SPACING

                elif current_key == "sell":
                    for crop_name, qty in list(self.crops.items()):
                        row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                        BTN_W, BTN_H, GAP, PAD = 58, row.h - 4, 6, 6
                        block_w = BTN_W + GAP + BTN_W + PAD
                        text_right = row.right - block_w
                        sell1   = pygame.Rect(text_right + PAD, row.y + 2, BTN_W, BTN_H)
                        sellall = pygame.Rect(sell1.right + GAP, row.y + 2, BTN_W, BTN_H)

                        if sell1.collidepoint((local_x, local_y)) and qty > 0:
                            self.crops[crop_name] -= 1; self.money += self.sell_prices.get(crop_name, 1); return True
                        if sellall.collidepoint((local_x, local_y)) and qty > 0:
                            amt = self.crops[crop_name]; self.crops[crop_name] = 0; self.money += amt * self.sell_prices.get(crop_name, 1); return True
                        y_cursor += OPTION_H + OPTION_SPACING

                else:  # inventory
                    sect = current_key.split(":")[1]
                    if sect == "tools":
                        for i, _t in enumerate(self.tools_owned):
                            row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                            equip_btn = pygame.Rect(row.right - 80, row.y + 2, 76, row.h - 4)
                            if equip_btn.collidepoint((local_x, local_y)):
                                self.equipped_tool = i
                                return True
                            y_cursor += OPTION_H + OPTION_SPACING
                    else:
                        # seeds/dirt/ferts/crops are read-only here
                        return True

            # If we got here and click was inside panel, consume it
            if shop_rect.collidepoint(event.pos):
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.scroll_dragging:
                self.scroll_dragging = False
                self.drag_key = None
                return True

        elif event.type == pygame.MOUSEMOTION and self.scroll_dragging and self.active and self.drag_key is not None:
            content_h = self._calc_content_height(self.drag_key)
            max_scroll = max(0, content_h - content_clip.h)
            if max_scroll > 0:
                delta = event.pos[1] - self.drag_anchor_y
                track_h = content_clip.h
                ratio = content_clip.h / max(1, content_h)
                thumb_h = max(24, int(track_h * ratio))
                effective = max(1, track_h - thumb_h)
                delta_ratio = delta / effective
                new_scroll = self.drag_anchor_scroll + delta_ratio * max_scroll
                self.scroll[self.drag_key] = clamp(new_scroll, 0, max_scroll)
            return True

        elif event.type == pygame.MOUSEWHEEL and self.active:
            mx, my = pygame.mouse.get_pos()
            if content_clip.collidepoint((mx, my)):
                current_key = "sell" if self.active_tab=="sell" else (f"buy:{self.buy_subtab}" if self.active_tab=="buy" else f"inv:{self.inv_subtab}")
                content_h = self._calc_content_height(current_key)
                max_scroll = max(0, content_h - content_clip.h)
                if max_scroll > 0:
                    self.scroll[current_key] = clamp(self.scroll[current_key] - event.y * SCROLL_STEP, 0, max_scroll)
                return True

        return False  # not consumed
