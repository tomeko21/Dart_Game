import pygame
from config.consts import *
from components.ui_utils import draw_glass_rect

class Button:
    def __init__(self, x, y, w, h, text, font, action_color=GOLD):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.action_color = action_color
        self.is_hovered = False

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        draw_glass_rect(
            surface, 
            self.rect, 
            radius=30, 
            is_active=self.is_hovered,
            color_active=self.action_color
        )

        text_col = BLACK if self.is_hovered else WHITE
        
        txt_surf = self.font.render(self.text, True, text_col)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False