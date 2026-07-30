import pygame
import time
import os
from config.consts import *

class PickupBar:
    def __init__(self, cx, cy, radius, is_flipped=False):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.diameter = radius * 2
        
        self.finish_time = None 
        
        # Background
        self.surf_base = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.surf_base, (0, 0, 0, 100), (radius, radius), radius)
        pygame.draw.circle(self.surf_base, (255, 255, 255, 150), (radius, radius), radius, 3)

        # Progress
        self.surf_fill = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.surf_fill, (50, 255, 50, 150), (radius, radius), radius)

        # Icon
        self.icon_surf = self._load_and_prep_icon(is_flipped)

    def _load_and_prep_icon(self, is_flipped):
        try:
            img = pygame.image.load(HAND_IMG).convert_alpha()
            target_size = int(self.diameter * 0.6)
            img = pygame.transform.smoothscale(img, (target_size, target_size))
            
            if is_flipped:
                img = pygame.transform.flip(img, True, False)
                
            return img
            
        except FileNotFoundError:
            print(f"BŁĄD: Nie znaleziono pliku rysuje kwadrat.")
            fallback = pygame.Surface((40, 40))
            fallback.fill((255, 0, 0))
            return fallback

    def draw(self, surface, progress):
        if progress < 1.0:
            self.finish_time = None        
        else:
            if self.finish_time is None:
                self.finish_time = time.time()
            if time.time() - self.finish_time > 1.0:
                return

        dest_pos = (self.cx - self.radius, self.cy - self.radius)

        #Base shape
        surface.blit(self.surf_base, dest_pos)

        #Progress
        if progress > 0:
            draw_progress = min(progress, 1.0)
            fill_height = int(self.diameter * draw_progress)
            
            area_rect = pygame.Rect(0, self.diameter - fill_height, self.diameter, fill_height)
            
            dest_y_offset = self.diameter - fill_height
            final_dest = (dest_pos[0], dest_pos[1] + dest_y_offset)
            
            surface.blit(self.surf_fill, final_dest, area=area_rect)

        #Icon
        if self.icon_surf:
            icon_rect = self.icon_surf.get_rect(center=(self.cx, self.cy))
            surface.blit(self.icon_surf, icon_rect)