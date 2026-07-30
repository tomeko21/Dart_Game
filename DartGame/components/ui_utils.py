import pygame
from config.consts import *

def draw_glass_rect(surface, rect, radius=15, is_active=False, is_hovered=False, color_active=NEON_GREEN, color_hovered=(80, 80, 90, 200), color_default=GLASS_FILL):
    shape_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    if is_active:
        fill_col = (*color_active[:3], 150)
        border_col = color_active
        border_width = 3
    elif is_hovered:
        fill_col = color_hovered
        border_col = (255, 255, 255, 150)
        border_width = 2
    else:
        fill_col = color_default
        border_col = GLASS_BORDER
        border_width = 2

    pygame.draw.rect(shape_surf, fill_col, shape_surf.get_rect(), border_radius=radius)
    pygame.draw.rect(shape_surf, border_col, shape_surf.get_rect(), border_width, border_radius=radius)
    surface.blit(shape_surf, rect)