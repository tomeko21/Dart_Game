import pygame
from config.consts import *
from components.button import Button
from components.image_selector import ImageSelector
from components.number_input import NumberInput
from components.option_groups import OptionGroup
from components.button import Button

class MenuView:
    def __init__(self, screen):
        self.screen = screen
        window_w, window_h = self.screen.get_size()
        center_x = window_w // 2
        
        #Czcionka        
        title_size = int(window_h * FONT_SCALE_TITLE) 
        self.font_title = pygame.font.SysFont(FONT_NAME_MAIN, title_size, bold=True)
        self.font_ui = pygame.font.SysFont(FONT_NAME_MAIN, FONT_SIZE_UI_BASE)
        self.font_item = pygame.font.SysFont("Arial", 28)

        #Elementy
        img_box_w = int(window_w * 0.25)
        img_box_h = int(window_h * 0.30)
        
        img_box_left_x_pos = int(window_w * 0.25) - img_box_w // 2
        img_box_right_x_pos = int(window_w * 0.75) - img_box_w // 2
        img_box_y_pos = int(window_h * 0.15)

        self.sel_board = ImageSelector(img_box_left_x_pos, img_box_y_pos, img_box_w, img_box_h, 
                                       "Board Skin", BOARD_SKINS, self.font_ui)
                                       
        self.sel_bg = ImageSelector(img_box_right_x_pos, img_box_y_pos, img_box_w, img_box_h, 
                                    "Background Skin", BACKGROUND_SKINS, self.font_ui)
        
        #SKIN LOTKI

        
        start_y_remaining = img_box_y_pos + img_box_h + 20

        self.sel_input = OptionGroup(center_x - 200, start_y_remaining + 230, 400, 40, 
                                     ["Camera", "Touchpad"], 1, self.font_ui)
        
        self.num_players = NumberInput(center_x, start_y_remaining + 50, "Players Count", 1, 10, self.font_ui)

        self.sel_mode = OptionGroup(center_x - 200, start_y_remaining + 100, 400, 40, 
                                    ["LOW (Exact 0)", "HIGH (Below 0)"], 0, self.font_ui)
        
        self.sel_points = OptionGroup(center_x - 250, start_y_remaining + 160, 500, 40, 
                                      [301, 501, 701, 901], 1, self.font_ui)

        self.btn_back = Button(40, window_h - 90, 200, 60, "POWRÓT", self.font_item, RED)

        btn_w, btn_h = 260, 60
        btn_y = window_h - btn_h - 30
        self.btn_start = Button(center_x - btn_w//2, btn_y, btn_w, btn_h, "START GAME", self.font_ui)

    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.fill(COLOR_MENU_BG)
            
            # Tytuł
            title = self.font_title.render("GAME SETUP", True, WHITE)
            title_rect = title.get_rect(center=(self.screen.get_width()//2, self.screen.get_height() * 0.08))
            self.screen.blit(title, title_rect)

            # Rysowanie komponentów
            self.sel_board.draw(self.screen)
            self.sel_bg.draw(self.screen)
            self.num_players.draw(self.screen)
            self.sel_mode.draw(self.screen)
            self.sel_points.draw(self.screen)

            #start and exit buttons
            self.btn_start.draw(self.screen)
            self.btn_back.draw(self.screen)
            #touchpad/camera selection button
            self.sel_input.draw(self.screen)

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "EXIT_APP"

                if pygame.mouse.get_pressed()[0]:
                    if self.btn_back.rect.collidepoint(mouse_pos):
                        return "BACK_TO_TITLE"
                
                self.sel_board.handle_event(event)
                self.sel_bg.handle_event(event)
                self.num_players.handle_event(event)
                self.sel_mode.handle_event(event)
                self.sel_points.handle_event(event)
                self.sel_input.handle_event(event)
                
                if self.btn_start.is_clicked(event):
                    mode_str = self.sel_mode.get_selected()
                    input_choice = self.sel_input.get_selected()
                    return {
                        "action": "START",
                        "board_skin": self.sel_board.get_selected(),
                        "bg_skin": self.sel_bg.get_selected(),
                        "dart_skin": "", #dodać
                        "players_count": self.num_players.get_value(),
                        "game_mode": "LOW" if "LOW" in mode_str else "HIGH",
                        "start_score": self.sel_points.get_selected(),
                        "input_method": input_choice
                    }

            pygame.display.flip()