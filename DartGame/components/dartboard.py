import pygame
import math
from config.consts import *

class Dartboard:
    def __init__(self, center_pos, font, image_path=None):
        self.cx, self.cy = center_pos
        self.font = font
        self.image = None
        self.rect = None
        
        if image_path:
            try:
                raw_img = pygame.image.load(image_path).convert_alpha()
                d = (R_BOARD_EDGE + 5) * 2
                self.image = pygame.transform.smoothscale(raw_img, (d, d))
                self.rect = self.image.get_rect(center=(self.cx, self.cy))
            except (FileNotFoundError, pygame.error):
                self.image = None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:

            pygame.draw.circle(screen, (20,20,20), (self.cx+5, self.cy+5), R_BOARD_EDGE+20)
            pygame.draw.circle(screen, BLACK, (self.cx, self.cy), R_BOARD_EDGE+20)
            
            step = 360 / 20
            rot = -90 - step/2
            
            for i in range(20):
                sa = math.radians(rot + i*step)
                ea = math.radians(rot + (i+1)*step)
                pts = [(self.cx, self.cy)]
                for j in range(12): # Łuk
                    a = sa + (ea - sa) * j / 11
                    pts.append((self.cx + math.cos(a) * R_BOARD_EDGE, self.cy + math.sin(a) * R_BOARD_EDGE))
                
                col = (230,230,210) if i%2==0 else BLACK 
                if i%2 != 0: col = (20, 20, 20)
                
                pygame.draw.polygon(screen, col, pts)
                
                # Liczby
                mid = (sa+ea)/2
                tx = self.cx + math.cos(mid)*(R_BOARD_EDGE+30)
                ty = self.cy + math.sin(mid)*(R_BOARD_EDGE+30)
                txt = self.font.render(str(SECTOR_VALUES[i]), True, WHITE)
                screen.blit(txt, txt.get_rect(center=(tx, ty)))
            
            # Pierścienie
            pygame.draw.circle(screen, RED, (self.cx, self.cy), R_OUTER_RING_END, 2)
            pygame.draw.circle(screen, GREEN, (self.cx, self.cy), R_INNER_RING_END, 2)
            pygame.draw.circle(screen, GREEN, (self.cx, self.cy), R_OUTER_BULL)
            pygame.draw.circle(screen, RED, (self.cx, self.cy), R_BULLSEYE)