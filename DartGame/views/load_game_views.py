import pygame
from config.consts import *
from components.button import Button
from components.ui_utils import draw_glass_rect
from game.save_game import get_all_saves

class LoadGameView:
    def __init__(self, screen):
        self.screen = screen
        self.window_w, self.window_h = self.screen.get_size()
        
        self.font_title = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_item = pygame.font.SysFont("Arial", 28)
        self.font_desc = pygame.font.SysFont("Arial", 20)
        
        # listę zapisów
        self.saves = get_all_saves()
        
        # UI
        self.btn_back = Button(40, self.window_h - 90, 200, 60, "POWRÓT", self.font_item, RED)
        
        self.scroll_y = 0
        self.item_height = 100
        self.gap = 15
        
        self.list_area = pygame.Rect(100, 120, self.window_w - 200, self.window_h - 240)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            # tło 
            self.screen.fill((20, 20, 25))
            
            title = self.font_title.render("HISTORIA GIER", True, NEON_BLUE)
            self.screen.blit(title, (self.window_w//2 - title.get_width()//2, 40))
            
            self.screen.set_clip(self.list_area)
            
            mouse_pos = pygame.mouse.get_pos()
            click_detected = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "EXIT_APP"
                
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll_y += event.y * 30
                    # ograniczenia scrollowania
                    max_scroll = 0
                    min_scroll = -(len(self.saves) * (self.item_height + self.gap) - self.list_area.height)
                    if min_scroll > 0: min_scroll = 0
                    
                    self.scroll_y = max(min_scroll, min(max_scroll, self.scroll_y))

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_detected = True
            
            start_y = self.list_area.y + self.scroll_y
            
            for i, save in enumerate(self.saves):
                item_y = start_y + i * (self.item_height + self.gap)
                
                #krok optymalizacyjny
                if item_y + self.item_height < self.list_area.top or item_y > self.list_area.bottom:
                    continue
                
                rect = pygame.Rect(self.list_area.x, item_y, self.list_area.width, self.item_height)
                
                is_hovered = rect.collidepoint(mouse_pos)
                draw_glass_rect(self.screen, rect, radius=10, is_active=is_hovered, color_active=BLUE_UI)
                

                date_txt = self.font_item.render(save["timestamp"], True, GOLD)
                self.screen.blit(date_txt, (rect.x + 20, rect.y + 15))
                
                mode_str = f"Tryb: {save['mode']} {save['score_type']} pts"
                mode_txt = self.font_item.render(mode_str, True, WHITE)
                self.screen.blit(mode_txt, (rect.x + 20, rect.y + 55))
                
                p_txt = self.font_item.render(f"Graczy: {save['players']}", True, CYAN)
                p_rect = p_txt.get_rect(midright=(rect.right - 30, rect.centery))
                self.screen.blit(p_txt, p_rect)
                
                if click_detected and is_hovered:
                    self.screen.set_clip(None)
                    return {
                        "action": "LOAD_GAME",
                        "data": save["full_data"],
                        "filename": save["filename"]
                    }

            self.screen.set_clip(None)
            
            pygame.draw.rect(self.screen, GRAY_LIGHT, self.list_area, 2)
            
            self.btn_back.draw(self.screen)
            
            if pygame.mouse.get_pressed()[0]:
                if self.btn_back.rect.collidepoint(mouse_pos):
                     return "BACK_TO_TITLE"

            pygame.display.flip()
            clock.tick(60)