import pygame
from config.consts import *


class MessageSystem:
    def __init__(self, font_regular, font_big):
        self.font = font_regular
        self.font_big = font_big

        self.overlay_surface = pygame.Surface((APP_WIDTH, APP_HEIGHT))
        self.overlay_surface.set_alpha(180)
        self.overlay_surface.fill((0, 0, 0))

    def show_blocking_message(self, surface, text, subtext=""):
        surface.blit(self.overlay_surface, (0, 0))
        
        # Tekst główny
        txt = self.font_big.render(text, True, RED)
        rect = txt.get_rect(center=(APP_WIDTH//2, APP_HEIGHT//2 - 30))
        surface.blit(txt, rect)
        
        # Podtytuł
        if subtext:
            sub = self.font.render(subtext, True, WHITE)
            sub_rect = sub.get_rect(center=(APP_WIDTH//2, APP_HEIGHT//2 + 30))
            surface.blit(sub, sub_rect)

    def show_top_hint(self, surface, text, color=CYAN):
        txt = self.font.render(text, True, color)
        rect = txt.get_rect(center=(APP_WIDTH//2, 100))
        
        bg_rect = rect.inflate(20, 10)
        pygame.draw.rect(surface, (0,0,0, 100), bg_rect, border_radius=5)
        surface.blit(txt, rect)