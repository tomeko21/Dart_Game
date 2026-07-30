import pygame
import os
from config.consts import *
from components.button import Button
from components.ui_utils import draw_glass_rect

class TitleView:
    def __init__(self, screen):
        self.screen = screen
        self.window_w, self.window_h = self.screen.get_size()
        
        self.font_title = pygame.font.SysFont(FONT_NAME_MAIN, 100, bold=True)
        self.font_btn = pygame.font.SysFont(FONT_NAME_MAIN, 40)

        self.bg_image = None
        try:
            img_path = os.path.join("assets", "title_background.jpg")
            background = pygame.image.load(img_path).convert()
            self.bg_image = pygame.transform.smoothscale(background, (self.window_w, self.window_h))
        except FileNotFoundError:
            self.bg_image = None
        
        btn_w, btn_h = 300, 70
        cx = self.window_w // 2
        cy = self.window_h // 2
        
        gap = 90
        
        self.btn_new_game = Button(cx - btn_w//2, cy, btn_w, btn_h, "NOWA GRA", self.font_btn, NEON_GREEN)
        self.btn_load_game = Button(cx - btn_w//2, cy + gap, btn_w, btn_h, "WCZYTAJ GRĘ", self.font_btn, CYAN)
        self.btn_exit = Button(cx - btn_w//2, cy + gap*2, btn_w, btn_h, "WYJDŹ", self.font_btn, RED)
        
        #Title
        self.title_surf = self.font_title.render("DART GAME", True, NEON_BLUE)
        self.title_rect = self.title_surf.get_rect(center=(cx, cy - 120))

    def run(self):
        running = True
        while running:
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill((15, 15, 20))
            
            title_bg_rect = self.title_rect.inflate(100, 60)
            draw_glass_rect(self.screen, title_bg_rect, radius=30, color_default=(30, 30, 40, 150))
            
            #Text
            self.screen.blit(self.title_surf, self.title_rect)
            
            #Buttons
            self.btn_new_game.draw(self.screen)
            self.btn_load_game.draw(self.screen)
            self.btn_exit.draw(self.screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "EXIT"
                
                if self.btn_new_game.is_clicked(event):
                    return "NEW_GAME"
                
                if self.btn_load_game.is_clicked(event):
                    return "LOAD_GAME_MENU"
                
                if self.btn_exit.is_clicked(event):
                    return "EXIT"
            
            pygame.display.flip()