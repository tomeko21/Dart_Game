import pygame
from views.menu_view import MenuView
from views.game_view import GameView
from config.consts import APP_WIDTH, APP_HEIGHT

from views.title_screen import TitleView
from views.load_game_views import LoadGameView 
from config.consts import APP_WIDTH, APP_HEIGHT

def main():
    pygame.init()
    
    #App window size
    try:
        screen_menu = pygame.display.set_mode((APP_WIDTH, APP_HEIGHT))
    except pygame.error:
        screen_menu = pygame.display.set_mode((1280, 720))
        
    pygame.display.set_caption("Dart game")
    
    current_state = "TITLE"
    
    while current_state != "EXIT":
        
        if current_state == "TITLE":
            view = TitleView(screen_menu)
            action = view.run()
            
            if action == "NEW_GAME":
                current_state = "MENU_SETUP"
            elif action == "LOAD_GAME_MENU":
                current_state = "LOAD_MENU"
            elif action == "EXIT":
                current_state = "EXIT"
        
        elif current_state == "MENU_SETUP":
            view = MenuView(screen_menu)
            game_config = view.run()
            
            if game_config == "EXIT_APP":
                current_state = "EXIT"
            elif game_config == "BACK_TO_TITLE":
                current_state = "TITLE"
            elif isinstance(game_config, dict) and game_config.get("action") == "START":
                current_game_config = game_config
                current_state = "GAMEPLAY"
        elif current_state == "LOAD_MENU":
            view = LoadGameView(screen_menu)
            result = view.run()
            
            if result == "EXIT_APP":
                current_state = "EXIT"
            elif result == "BACK_TO_TITLE":
                current_state = "TITLE"
            elif isinstance(result, dict) and result.get("action") == "LOAD_GAME":
                saved_data = result["data"]
                
                current_game_config = {
                    "saved_data": saved_data,
                    "bg_skin": saved_data.get("bg_skin"),
                    "board_skin": saved_data.get("board_skin"),
                    "source_filename": result["filename"]
                }
                current_state = "GAMEPLAY"
                
        elif current_state == "GAMEPLAY":
            game = GameView(screen_menu, current_game_config)
            game.run()
            
            current_state = "TITLE"
            
            screen_menu = pygame.display.set_mode((APP_WIDTH, APP_HEIGHT))

            if game_config == "EXIT_APP":
                current_state = "EXIT"
            else:
                current_state = "TITLE"

    pygame.quit()


if __name__ == "__main__":
    main()