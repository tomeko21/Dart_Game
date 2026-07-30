import pygame
import math
from config.consts import *

class DebugRenderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def draw_calibration_grid(self, board_center):
        cx, cy = board_center
        
        #Circels
        circles = [
            (R_BULLSEYE, (255, 0, 255)),
            (R_OUTER_BULL, (255, 0, 255)),       
            (R_INNER_RING_START, (0, 255, 255)),
            (R_INNER_RING_END, (0, 255, 255)),   
            (R_OUTER_RING_START, (0, 255, 0)),
            (R_OUTER_RING_END, (0, 255, 0)),     
            (R_BOARD_EDGE, (255, 0, 0))
        ]

        for r, color in circles:
            pygame.draw.circle(self.screen, color, (cx, cy), r, 1)

        # Sectors
        for i in range(20):
            angle_deg = (i * 18) - 99 
            angle_rad = math.radians(angle_deg)
            
            end_x = cx + math.cos(angle_rad) * (R_BOARD_EDGE + 20)
            end_y = cy + math.sin(angle_rad) * (R_BOARD_EDGE + 20)
            
            pygame.draw.line(self.screen, (255, 255, 0), (cx, cy), (end_x, end_y), 1)
            
            # Point numbers
            mid_angle_rad = math.radians(angle_deg + 9)
            tx = cx + math.cos(mid_angle_rad) * (R_OUTER_RING_START - 20)
            ty = cy + math.sin(mid_angle_rad) * (R_OUTER_RING_START - 20)
            try:
                txt = self.font.render(str(SECTOR_VALUES[i]), True, (255, 255, 255))
                self.screen.blit(txt, (tx - 10, ty - 10))
            except: pass


    def draw_confidence_bar(self, data, window_w, window_h):
        conf = data.get("ai_confidence", 0.0)
        bar_w, bar_h = 300, 15
        cx, cy = window_w // 2, window_h - 30 
        
        # Bg
        pygame.draw.rect(self.screen, (30, 30, 30), (cx - bar_w//2, cy, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(self.screen, WHITE, (cx - bar_w//2, cy, bar_w, bar_h), 2, border_radius=5)
        
        # Fill
        fill_w = int(bar_w * conf)
        col = GREEN if conf > AI_CONFIDENCE_THRESHOLD else RED
        pygame.draw.rect(self.screen, col, (cx - bar_w//2 + 2, cy + 2, max(0, fill_w - 4), bar_h - 4), border_radius=3)
        
        # Progress line
        th_offset = int(bar_w * AI_CONFIDENCE_THRESHOLD)
        th_x = (cx - bar_w//2) + th_offset
        pygame.draw.line(self.screen, CYAN, (th_x, cy-5), (th_x, cy+bar_h+5), 2)
        
        # Txt
        txt = self.font.render(f"Confidence: {int(conf*100)}%", True, WHITE)
        self.screen.blit(txt, (cx - 40, cy - 25))


    def draw_skeleton(self, data):
        if data.get("skeleton"):
            s, e, w = data["skeleton"]
            pygame.draw.line(self.screen, CYAN, s, e, 4)
            pygame.draw.line(self.screen, MAGENTA, e, w, 4)