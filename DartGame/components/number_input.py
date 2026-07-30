import pygame
import time
from config.consts import *
from components.ui_utils import draw_glass_rect

class NumberInput:
    def __init__(self, cx, cy, label, min_val, max_val, font):
        self.cx = cx
        self.cy = cy
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = 1
        self.font = font
        
        self.btn_minus = pygame.Rect(cx - 60, cy, 40, 40)
        self.btn_plus = pygame.Rect(cx + 20, cy, 40, 40)
        
        self.error_msg = ""
        self.error_timer = 0

    def get_value(self):
        return self.value

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_minus.collidepoint(event.pos):
                if self.value > self.min_val: self.value -= 1
                else: self._err(f"Min: {self.min_val}")
            
            elif self.btn_plus.collidepoint(event.pos):
                if self.value < self.max_val: self.value += 1
                else: self._err(f"Max: {self.max_val}")

    def _err(self, msg):
        self.error_msg = msg
        self.error_timer = time.time() + 1.5

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        
        # Label
        lbl = self.font.render(self.label, True, NEON_BLUE)
        surface.blit(lbl, lbl.get_rect(center=(self.cx, self.cy - 30)))

        # Buttons
        hover_m = self.btn_minus.collidepoint(mouse_pos)
        hover_p = self.btn_plus.collidepoint(mouse_pos)

        draw_glass_rect(surface, self.btn_minus, radius=10, is_hovered=hover_m)
        draw_glass_rect(surface, self.btn_plus, radius=10, is_hovered=hover_p)

        t1 = self.font.render("-", True, WHITE)
        t2 = self.font.render("+", True, WHITE)
        surface.blit(t1, t1.get_rect(center=self.btn_minus.center))
        surface.blit(t2, t2.get_rect(center=self.btn_plus.center))

        # Values
        val_txt = self.font.render(str(self.value), True, WHITE)
        mid_x = (self.btn_minus.right + self.btn_plus.left) // 2
        surface.blit(val_txt, val_txt.get_rect(center=(mid_x, self.cy + 20)))

        # Error
        if time.time() < self.error_timer:
            err = pygame.font.SysFont("Arial", 18).render(self.error_msg, True, RED)
            surface.blit(err, err.get_rect(center=(mid_x, self.cy + 55)))