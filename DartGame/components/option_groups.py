import pygame
from config.consts import *
from components.ui_utils import draw_glass_rect

class OptionGroup:
    def __init__(self, x, y, w, h, options, default_idx, font):
        self.options = options
        self.selected_idx = default_idx
        self.font = font
        self.rects = []
        
        gap = 10
        total_gaps = (len(options) - 1) * gap
        btn_w = (w - total_gaps) // len(options)
        
        for i in range(len(options)):
            r = pygame.Rect(x + i*(btn_w + gap), y, btn_w, h)
            self.rects.append(r)

    def get_selected(self):
        return self.options[self.selected_idx]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected_idx = i

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        
        for i, r in enumerate(self.rects):
            is_selected = (i == self.selected_idx)
            is_hovered = r.collidepoint(mouse_pos)
            
            draw_glass_rect(surface, r, radius=15, is_active=is_selected, is_hovered=is_hovered)
            
            col = BLACK if is_selected else WHITE
            txt = self.font.render(str(self.options[i]), True, col)
            surface.blit(txt, txt.get_rect(center=r.center))