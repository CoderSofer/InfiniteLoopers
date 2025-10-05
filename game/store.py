# game/shop_popup.py
from __future__ import annotations
import pygame
from typing import Optional, Dict, List

# ---- Colors / layout ----
<<<<<<< Updated upstream
COL_PANEL_BG = (220, 220, 220)
COL_PANEL_BORDER = (0, 0, 0)
COL_BTN = (190, 190, 190)
COL_BTN_ACTIVE = (160, 160, 160)
=======
COL_PANEL_BG = (255, 255, 255)
COL_BTN = (78, 177, 78)
COL_BTN_ACTIVE = (0, 118, 0)
>>>>>>> Stashed changes
COL_GOOD = (100, 200, 100)
COL_BAD = (200, 80, 80)
COL_TEXT = (173, 109, 68)
COL_DISABLED = (180, 180, 180)
COL_SCROLL_TRACK = (210, 210, 210)
COL_SCROLL_THUMB = (150, 150, 150)

# Layout
OPTION_H = 22
OPTION_SPACING = 6
# Just a label now; actual size is computed responsively in _shop_rect
TAB_WIDTH = 640
TAB_HEADER_H = 72
SUBTAB_H = 28
PANEL_HEIGHT = 420
CONTENT_PAD = 8
SCROLL_STEP = 40

def clamp(v, lo, hi): return max(lo, min(hi, v))

def _find_by_name(items: List[Dict], name: str) -> int:
    for i, it in enumerate(items):
        if it.get("name") == name:
            return i
    return -1

class ShopPopup:
    """
    Separate Store (stock) vs Inventory (owned).
    - Store rows: {"name","price","stock", ...}
    - Inventory rows: {"name","qty", ...}
    """
    def __init__(self, fonts: Dict[str, pygame.font.Font] | None = None, *, money: int = 200):
        fonts = fonts or {}
        self.font_tab   = fonts.get('tab')   or pygame.font.SysFont(None, 18)
        self.font_title = fonts.get('title') or pygame.font.SysFont(None, 22)

        # -------- Store (coins needed + quantity available) --------
        self.store_seeds: List[Dict] = [
            {"name": "Carrot Seeds",   "price": 1,  "stock": 50},
            {"name": "Potato Seeds",   "price": 3,  "stock": 30},
            {"name": "Tomato Seeds",   "price": 9,  "stock": 25},
            {"name": "Cucumber Seeds", "price": 12, "stock": 15},
            {"name": "Lentil Seeds",   "price": 15, "stock": 5},
        ]
        self.store_dirt: List[Dict] = [
            {"name": "Loose & well-draining",           "price": 15, "stock": 12},
            {"name": "Rich & well-draining",            "price": 10, "stock": 20},
            {"name": "Deep & Loose",                    "price": 18, "stock": 8},
            {"name": "Loamy",                           "price": 22, "stock": 6},
            {"name": "Well-draining",                   "price": 25, "stock": 4},
        ]
        self.store_ferts: List[Dict] = [
            {"name": "Nitrogen", "price": 25, "stock": 6},
            {"name": "Phosphorus", "price": 35, "stock": 5},
            {"name": "Potassium", "price": 50, "stock": 3},
        ]
        self.store_tools: List[Dict] = [
            {"name": "Hoe",          "price": 40, "stock": 3, "color": (255,170,80)},
            {"name": "Watering Can", "price": 60, "stock": 2, "color": (120,200,255)},
            {"name": "Scythe",       "price": 85, "stock": 1, "color": (200,200,200)},
            {"name": "Axe",          "price": 75, "stock": 1, "color": (240,120,120)},
        ]

        # -------- Inventory --------
<<<<<<< Updated upstream
        self.inv_seeds: List[Dict] = []
        self.inv_dirt:  List[Dict] = []
=======
        self.inv_seeds: List[Dict] = [
            {"name": "Carrot Seeds",   "qty": 1, "price": 8},
            {"name": "Potato Seeds",   "qty": 0, "price": 12},
            {"name": "Tomato Seeds",   "qty": 0, "price": 6},
            {"name": "Cucumber Seeds", "qty": 0, "price": 10},
            {"name": "Lentil Seeds",  "qty": 0, "price": 20},]
>>>>>>> Stashed changes
        self.inv_ferts: List[Dict] = []
        self.inv_tools: List[Dict] = []
        self.inv_crops: List[Dict] = [
            {"name": "Carrot",   "qty": 3, "price": 8},
            {"name": "Potato",   "qty": 2, "price": 12},
            {"name": "Tomato",   "qty": 0, "price": 6},
            {"name": "Cucumber", "qty": 0, "price": 10},
            {"name": "Lentils",  "qty": 5, "price": 20},
        ]

        self.money = money
        self.equipped_tool: Optional[int] = None  # index into inv_tools

        # ---- UI state ----
        self.active = True
        self.active_tab = "buy"
        self.buy_subtab = "seeds"
        self.inv_subtab = "seeds"

        self.scroll = {
            "buy:seeds": 0, "buy:dirt": 0, "buy:ferts": 0, "buy:tools": 0,
            "sell": 0,
            "inv:seeds": 0, "inv:dirt": 0, "inv:ferts": 0, "inv:tools": 0, "inv:crops": 0,
        }
        self.scroll_dragging = False
        self.drag_key = None
        self.drag_anchor_y = 0
        self.drag_anchor_scroll = 0

    # ---------------- data helpers ----------------
    def _store_for(self, subtab: str) -> List[Dict]:
        return {"seeds": self.store_seeds, "dirt": self.store_dirt, "ferts": self.store_ferts, "tools": self.store_tools}[subtab]
    def _inv_for(self, subtab: str) -> List[Dict]:
        return {"seeds": self.inv_seeds, "dirt": self.inv_dirt, "ferts": self.inv_ferts, "tools": self.inv_tools, "crops": self.inv_crops}[subtab]
    def _owned_qty(self, inv_list: List[Dict], name: str) -> int:
        i = _find_by_name(inv_list, name); return 0 if i < 0 else int(inv_list[i].get("qty", 0))
    def _add_to_inventory(self, inv_list: List[Dict], name: str, delta: int, **extra):
        i = _find_by_name(inv_list, name)
        if i < 0: inv_list.append({"name": name, "qty": max(0, delta), **extra})
        else:     inv_list[i]["qty"] = max(0, inv_list[i]["qty"] + delta)
    def _dec_store_stock(self, store_list: List[Dict], name: str, delta: int = 1) -> bool:
        i = _find_by_name(store_list, name)
        if i >= 0 and store_list[i]["stock"] >= delta:
            store_list[i]["stock"] -= delta
            return True
        return False
    def _visible(self, items: List[Dict]) -> List[Dict]:
        return [it for it in items if it.get("qty", 0) > 0]

    # ---------------- geometry helpers ----------------
    def _grid_rect(self, g: Dict) -> pygame.Rect:
        grid_w = g["cols"] * g["tile_size"] + (g["cols"] - 1) * g["gap"]
        grid_h = g["rows"] * g["tile_size"] + (g["rows"] - 1) * g["gap"]
        return pygame.Rect(g["start_x"], g["start_y"], grid_w, grid_h)

    def _shop_rect(self, g: Dict, sw: int, sh: int) -> pygame.Rect:
        """Responsive sizing with generous minimums."""
        grid_w = g["cols"] * g["tile_size"] + (g["cols"] - 1) * g["gap"]
        grid_h = g["rows"] * g["tile_size"] + (g["rows"] - 1) * g["gap"]
        grid_r = pygame.Rect(g["start_x"], g["start_y"], grid_w, grid_h)

        # target ~60% of screen width, ~75% of height
        desired_w = int(sw * 0.60)
        desired_h = int(sh * 0.75)
        w = clamp(max(TAB_WIDTH, desired_w), 520, sw - 16)   # bigger minimums
        h = clamp(max(PANEL_HEIGHT, desired_h), 360, sh - 16)

        # prefer right of the grid
        x = grid_r.right + 16
        y = grid_r.top
        # try left if it doesn't fit
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
            shop_rect.w - 2 * CONTENT_PAD - 10,  # minus scrollbar
            shop_rect.h - (top - shop_rect.y) - CONTENT_PAD
        )

    def _calc_content_height(self, key: str) -> int:
        def rows(n): return n * (OPTION_H + OPTION_SPACING)
        if key == "sell": return rows(len(self._visible(self.inv_crops)))
        ktab, ksub = (key.split(":") + [""])[:2]
        if ktab == "buy": return rows(len(self._store_for(ksub)))
        if ktab == "inv": return rows(len(self._visible(self._inv_for(ksub))))
        return 0

    # ---------------- drawing primitives ----------------
    def _draw_tab_button(self, surface, rect, label, active):
<<<<<<< Updated upstream
        pygame.draw.rect(surface, COL_BTN_ACTIVE if active else COL_BTN, rect)
        pygame.draw.rect(surface, COL_PANEL_BORDER, rect, 2)
=======
        pygame.draw.rect(surface, COL_BTN_ACTIVE if active else COL_BTN, rect, border_radius=4)
>>>>>>> Stashed changes
        surface.blit(self.font_tab.render(label, True, COL_TEXT), (rect.x + 6, rect.y + 4))

    def _draw_subtabs(self, surface, shop_rect, current, y, include_crops=False):
        labels = [("seeds", "Seeds"), ("dirt", "Dirt"), ("ferts", "Fertilisers"), ("tools", "Tools")]
        if include_crops: labels.append(("crops", "Crops"))
        x = shop_rect.x + 8; w = 84; out = {}
        for key, label in labels:
            r = pygame.Rect(x, y, w, 24)
            self._draw_tab_button(surface, r, label, current == key)
            out[key] = r; x += w + 6
        return out

    def _draw_scrollbar(self, surface, key, content_clip, content_h):
        if content_h <= content_clip.h: return None
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

    # ---------------- PUBLIC: draw + events ----------------
    def draw(self, surface: pygame.Surface, grid_geom: Dict) -> None:
        if not self.active: return
        sw, sh = surface.get_size()
        shop_rect = self._shop_rect(grid_geom, sw, sh)

        pygame.draw.rect(surface, COL_PANEL_BG, shop_rect)
        pygame.draw.rect(surface, COL_PANEL_BORDER, shop_rect, 2)

        # Header
        surface.blit(self.font_title.render("Farm Shop", True, COL_TEXT), (shop_rect.x + 8, shop_rect.y + 8))
        close_size = 18
        close_rect = pygame.Rect(shop_rect.right - close_size - 8, shop_rect.y + 8, close_size, close_size)
        pygame.draw.rect(surface, COL_BAD, close_rect)
        x_txt = self.font_tab.render("X", True, (255, 255, 255))
        surface.blit(x_txt, x_txt.get_rect(center=close_rect.center))

        money_text = self.font_title.render(f"${self.money}", True, COL_TEXT)
        surface.blit(money_text, (close_rect.x - 8 - money_text.get_width(), shop_rect.y + 8))

        # Tabs
        tab_w, tab_h = 70, 24
        tab_y = shop_rect.y + 34
        buy_tab_rect  = pygame.Rect(shop_rect.x + 8, tab_y, tab_w, tab_h)
        sell_tab_rect = pygame.Rect(buy_tab_rect.right + 8, tab_y, tab_w, tab_h)
        inv_tab_rect  = pygame.Rect(sell_tab_rect.right + 8, tab_y, tab_w + 30, tab_h)
        self._draw_tab_button(surface, buy_tab_rect, "Buy", self.active_tab == "buy")
        self._draw_tab_button(surface, sell_tab_rect, "Sell", self.active_tab == "sell")
        self._draw_tab_button(surface, inv_tab_rect,  "Inventory", self.active_tab == "inventory")

        # Content frame
        if self.active_tab in ("buy", "inventory"):
            subtab_y = shop_rect.y + 34 + tab_h + 6
            current = self.buy_subtab if self.active_tab == "buy" else self.inv_subtab
            self._draw_subtabs(surface, shop_rect, current, subtab_y, include_crops=(self.active_tab == "inventory"))
            content_clip = self._content_clip(shop_rect, include_subtabs=True)
            current_key = f"{'buy' if self.active_tab=='buy' else 'inv'}:{current}"
        else:
            content_clip = self._content_clip(shop_rect, include_subtabs=False)
            current_key = "sell"

        pygame.draw.rect(surface, (235,235,235), content_clip)
        pygame.draw.rect(surface, COL_PANEL_BORDER, content_clip, 1)
        content_surf = surface.subsurface(content_clip)
        if content_clip.w <= 0 or content_clip.h <= 0: return

        y_cursor = -self.scroll[current_key]

        # ---- BUY (responsive right-aligned columns) ----
        if current_key.startswith("buy:"):
            sect = current_key.split(":")[1]
            store_list = self._store_for(sect)
            inv_list   = self._inv_for(sect)

            for it in store_list:
                row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                if row.bottom >= 0 and row.top <= content_clip.h:
                    pygame.draw.rect(content_surf, (240,240,240), row)
                    pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)

                    # Right-side layout: [ ... name ... | price | stock | BUY ]
                    # Right-side layout: [ ... name ... | price | stock | BUY ]
                    PAD = 6
                    BUY_W = 56
                    buy_btn = pygame.Rect(row.right - PAD - BUY_W, row.y + 2, BUY_W, row.h - 4)

                    # render texts
                    price_s = self.font_tab.render(f"${it['price']}", True, COL_TEXT)
                    price_x = buy_btn.x - PAD - price_s.get_width()

                    stock_s = self.font_tab.render(f"Stock: {it['stock']}", True, COL_TEXT)
                    stock_x = price_x - PAD - stock_s.get_width()   # <-- use stock_s width

                    # optional icon + name (unchanged)
                    x_text = row.x + 6
                    if sect == "tools" and "color" in it:
                        icon = pygame.Rect(row.x + 6, row.y + 3, 16, 16)
                        pygame.draw.rect(content_surf, it["color"], icon)
                        x_text = icon.right + 6

                    # draw price and stock in the new order
                    content_surf.blit(price_s, (price_x, row.y + 2))
                    content_surf.blit(stock_s, (stock_x, row.y + 2))

                    # "Own:" goes to the left of whichever (price/stock) is leftmost
                    owned = self._owned_qty(inv_list, it["name"])
                    own_s = self.font_tab.render(f"Own: {owned}", True, COL_TEXT)
                    anchor_x = min(price_x, stock_x)
                    own_x = anchor_x - PAD - own_s.get_width()
                    if own_x > x_text + 80:
                        content_surf.blit(own_s, (own_x, row.y + 2))

                    # name
                    content_surf.blit(self.font_tab.render(it["name"], True, COL_TEXT), (x_text, row.y + 2))

                    # buy button (unchanged)
                    can_buy = (self.money >= it["price"]) and (it["stock"] > 0)
                    pygame.draw.rect(content_surf, COL_GOOD if can_buy else COL_DISABLED, buy_btn)
                    pygame.draw.rect(content_surf, COL_PANEL_BORDER, buy_btn, 1)
                    content_surf.blit(self.font_tab.render("Buy", True, COL_TEXT), (buy_btn.x + 12, buy_btn.y + 2))

                y_cursor += OPTION_H + OPTION_SPACING

        # ---- SELL (inventory crops only) ----
        elif current_key == "sell":
            for it in self._visible(self.inv_crops):
                row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                if row.bottom >= 0 and row.top <= content_clip.h:
                    pygame.draw.rect(content_surf, (240,240,240), row)
                    pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)

                    BTN_W, BTN_H, GAP, PAD = 70, row.h - 4, 6, 6
                    block_w = BTN_W + GAP + BTN_W + PAD
                    text_right = row.right - block_w

                    content_surf.blit(self.font_tab.render(it["name"], True, COL_TEXT), (row.x + 6, row.y + 2))
                    content_surf.blit(self.font_tab.render(f"x{it['qty']}", True, COL_TEXT), (row.x + 160, row.y + 2))
                    price_s = self.font_tab.render(f"${it['price']} each", True, COL_TEXT)
                    content_surf.blit(price_s, (text_right - price_s.get_width() - 6, row.y + 2))

                    can_sell = it["qty"] > 0
                    sell1   = pygame.Rect(text_right + PAD,  row.y + 2, BTN_W, BTN_H)
                    sellall = pygame.Rect(sell1.right + GAP, row.y + 2, BTN_W, BTN_H)
                    for r, label in ((sell1,"Sell 1"), (sellall,"Sell All")):
                        pygame.draw.rect(content_surf, COL_BTN if can_sell else COL_DISABLED, r)
                        pygame.draw.rect(content_surf, COL_PANEL_BORDER, r, 1)
                        content_surf.blit(self.font_tab.render(label, True, COL_TEXT), (r.x + 8, r.y + 2))
                y_cursor += OPTION_H + OPTION_SPACING

        # ---- INVENTORY ----
        else:
            sect = current_key.split(":")[1]
            inv_list = self._visible(self._inv_for(sect))

            if sect in ("seeds", "dirt", "ferts"):
                for it in inv_list:
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(it["name"], True, COL_TEXT), (row.x + 6, row.y + 2))
                        content_surf.blit(self.font_tab.render(f"x{it['qty']}", True, COL_TEXT), (row.x + 200, row.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "crops":
                for it in inv_list:
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        content_surf.blit(self.font_tab.render(it["name"], True, COL_TEXT), (row.x + 6, row.y + 2))
                        qty_lbl = self.font_tab.render(f"x{it['qty']}", True, COL_TEXT)
                        content_surf.blit(qty_lbl, (row.right - qty_lbl.get_width() - 6, row.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

            elif sect == "tools":
                for i_abs, it in enumerate(inv_list):
                    row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                    if row.bottom >= 0 and row.top <= content_clip.h:
                        pygame.draw.rect(content_surf, (240,240,240), row); pygame.draw.rect(content_surf, COL_PANEL_BORDER, row, 1)
                        icon = pygame.Rect(row.x + 6, row.y + 3, 16, 16)
                        pygame.draw.rect(content_surf, it.get("color", (200,200,200)), icon)
                        content_surf.blit(self.font_tab.render(it["name"], True, COL_TEXT), (icon.right + 6, row.y + 2))
                        is_eq = (self.equipped_tool == i_abs)
                        btn = pygame.Rect(row.right - 90, row.y + 2, 86, row.h - 4)
                        pygame.draw.rect(content_surf, COL_BTN_ACTIVE if is_eq else COL_BTN, btn)
                        pygame.draw.rect(content_surf, COL_PANEL_BORDER, btn, 1)
                        content_surf.blit(self.font_tab.render("Equipped" if is_eq else "Equip", True, COL_TEXT), (btn.x + 6, btn.y + 2))
                    y_cursor += OPTION_H + OPTION_SPACING

        content_h = self._calc_content_height(current_key)
        self._draw_scrollbar(surface, current_key, self._content_clip(shop_rect, include_subtabs=(self.active_tab in ("buy","inventory"))), content_h)

    def handle_event(self, event: pygame.event.Event, grid_geom: Dict, sw: int = None, sh: int = None) -> bool:
        if not self.active: return False
        if sw is None or sh is None:
            surf = pygame.display.get_surface()
            sw, sh = surf.get_size() if surf else (800, 600)

        shop_rect = self._shop_rect(grid_geom, sw, sh)
        include_sub = (self.active_tab in ("buy", "inventory"))
        content_clip = self._content_clip(shop_rect, include_subtabs=include_sub)

        close_size = 18
        close_rect = pygame.Rect(shop_rect.right - close_size - 8, shop_rect.y + 8, close_size, close_size)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if close_rect.collidepoint(event.pos):
                self.active = False
                self.scroll_dragging = False
                self.drag_key = None
                return True

            # Tabs
            tab_w, tab_h = 70, 24
            tab_y = shop_rect.y + 34
            buy_tab_rect  = pygame.Rect(shop_rect.x + 8, tab_y, tab_w, tab_h)
            sell_tab_rect = pygame.Rect(buy_tab_rect.right + 8, tab_y, tab_w, tab_h)
            inv_tab_rect  = pygame.Rect(sell_tab_rect.right + 8, tab_y, tab_w + 30, tab_h)
            if buy_tab_rect.collidepoint(event.pos): self.active_tab = "buy"; return True
            if sell_tab_rect.collidepoint(event.pos): self.active_tab = "sell"; return True
            if inv_tab_rect.collidepoint(event.pos):  self.active_tab = "inventory"; return True

            # Subtabs
            if include_sub:
                sub_y = shop_rect.y + 34 + tab_h + 6
                labels = [("seeds","Seeds"), ("dirt","Dirt"), ("ferts","Fertilisers"), ("tools","Tools")]
                if self.active_tab == "inventory": labels.append(("crops","Crops"))
                x = shop_rect.x + 8; w = 84
                for key, _label in labels:
                    r = pygame.Rect(x, sub_y, w, 24)
                    if r.collidepoint(event.pos):
                        if self.active_tab == "buy": self.buy_subtab = key
                        else: self.inv_subtab = key
                        return True
                    x += w + 6

            # Scrollbar drag start?
            current_key = "sell" if self.active_tab == "sell" else (f"buy:{self.buy_subtab}" if self.active_tab=="buy" else f"inv:{self.inv_subtab}")
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

                # BUY click
                if current_key.startswith("buy:"):
                    sect = current_key.split(":")[1]
                    store_list = self._store_for(sect)
                    inv_list   = self._inv_for(sect)
                    for it in store_list:
                        row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                        PAD = 6; BUY_W = 56
                        buy_btn = pygame.Rect(row.right - PAD - BUY_W, row.y + 2, BUY_W, row.h - 4)
                        if buy_btn.collidepoint((local_x, local_y)) and self.money >= it["price"] and it["stock"] > 0:
                            if self._dec_store_stock(store_list, it["name"], 1):
                                self.money -= it["price"]
                                extra = {"color": it.get("color", (200,200,200))} if sect == "tools" else {}
                                self._add_to_inventory(inv_list, it["name"], +1, **extra)
                                if sect == "tools" and self.equipped_tool is None:
                                    self.equipped_tool = _find_by_name(self.inv_tools, it["name"])
                            return True
                        y_cursor += OPTION_H + OPTION_SPACING

                # SELL click
                elif current_key == "sell":
                    for it in self._visible(self.inv_crops):
                        row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                        BTN_W, BTN_H, GAP, PAD = 58, row.h - 4, 6, 6
                        block_w = BTN_W + GAP + BTN_W + PAD
                        text_right = row.right - block_w
                        sell1   = pygame.Rect(text_right + PAD, row.y + 2, BTN_W, BTN_H)
                        sellall = pygame.Rect(sell1.right + GAP, row.y + 2, BTN_W, BTN_H)
                        if sell1.collidepoint((local_x, local_y)) and it["qty"] > 0:
                            it["qty"] -= 1; self.money += it["price"]; return True
                        if sellall.collidepoint((local_x, local_y)) and it["qty"] > 0:
                            amt = it["qty"]; it["qty"] = 0; self.money += amt * it["price"]; return True
                        y_cursor += OPTION_H + OPTION_SPACING

                # INVENTORY clicks (equip tools)
                else:
                    sect = current_key.split(":")[1]
                    if sect == "tools":
                        for i_abs, _t in enumerate(self._visible(self.inv_tools)):
                            row = pygame.Rect(0, y_cursor, content_clip.w, OPTION_H)
                            equip_btn = pygame.Rect(row.right - 90, row.y + 2, 86, row.h - 4)
                            if equip_btn.collidepoint((local_x, local_y)):
                                name = _t["name"]
                                self.equipped_tool = _find_by_name(self.inv_tools, name)
                                return True
                            y_cursor += OPTION_H + OPTION_SPACING
                    else:
                        return True

            if shop_rect.collidepoint(event.pos): return True

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

        return False
