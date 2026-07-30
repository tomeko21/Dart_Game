import math
import pygame
import cv2
import numpy as np
import time
import random
from config.consts import *
from game.input_handler import SmartController
from game.scoring import calculate_score
from components.dartboard import Dartboard
from components.ui_utils import draw_glass_rect
from components.pickup_bar import PickupBar
from game.save_game import save_game_state
from components.button import Button
from game.save_game import save_game_state, delete_save_file
from game.debug_utils import DebugRenderer

class GameView:
    def __init__(self, screen, game_config):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.window_w, self.window_h = self.screen.get_size()

        self.debug = False
        self.source_filename = game_config.get("source_filename")
        self.config = game_config
        self.clock = pygame.time.Clock()
        
        # Background
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_big = pygame.font.SysFont("Arial", 64, bold=True)

        self.debug_renderer = DebugRenderer(self.screen, self.font)
        self._load_background(game_config.get("bg_skin"))
      
        offset_x = -1
        offset_y = -8
        self.board_center = (self.window_w // 2 + offset_x, self.window_h // 2 + offset_y)
        self.board = Dartboard((self.window_w // 2, self.window_h // 2), self.font, image_path=game_config.get("board_skin"))
        
        # --- Controller Initialization ---
        self.input_method = game_config.get("input_method", "Touchpad")
        # Only turn on the camera hardware if we are in Camera mode
        self.ctrl = SmartController(use_camera=(self.input_method == "Camera"))

        saved_data = game_config.get("saved_data")
        
        if saved_data:
            self.scores = saved_data["scores"]
            self.current_player_idx = saved_data["current_player"]
            self.game_mode = saved_data["game_mode"]
            self.num_players = saved_data["num_players"]
            self.start_score = saved_data["start_score"]
            if "bg_skin" in saved_data: 
                self._load_background(saved_data["bg_skin"])
        else:
            self.num_players = game_config["players_count"]
            self.start_score = game_config["start_score"]
            self.game_mode = game_config["game_mode"]
            
            initial = self.start_score if self.game_mode == "LOW" else 0
            self.scores = [initial] * self.num_players
            self.current_player_idx = 0

        # Buttons
        self.btn_pause_trigger = Button(self.window_w - 140, 20, 120, 50, "PAUSE", self.font, NEON_BLUE)

        cx, cy = self.window_w // 2, self.window_h // 2
        btn_w, btn_h = 300, 60
        self.btn_resume = Button(cx - btn_w//2, cy - 80, btn_w, btn_h, "WZNÓW", self.font, NEON_GREEN)
        self.btn_save = Button(cx - btn_w//2, cy, btn_w, btn_h, "ZAPISZ I WYJDŹ", self.font, GOLD)
        self.btn_exit = Button(cx - btn_w//2, cy + 80, btn_w, btn_h, "WYJDŹ", self.font, RED)

        # Camera Preview Box
        self.cam_w, self.cam_h = CAM_PREVIEW_SIZE
        self.cam_x = self.window_w - self.cam_w - 20
        self.cam_y = self.window_h- self.cam_h - 20
        
        # Pickup bars
        self.bar_left = PickupBar(80, self.window_h - 80, 40, is_flipped=False)
        self.bar_right = PickupBar(self.cam_x - 60, self.window_h - 80, 40, is_flipped=True)
        
        self.state = "PLAY"
        self.message = ""
        self.msg_timer = 0

        # Mouse/Touchpad vars
        self.mouse_phase = "AIM"
        self.mouse_aim_pos = (0, 0)
        self.mouse_lock_pos = None
        self.power_drag_start = None
        self.current_power = 0.0

    def _load_background(self, path):
        if path:
            try:
                bg = pygame.image.load(path).convert()
                self.bg_image = pygame.transform.smoothscale(bg, (self.window_w, self.window_h))
            except: self.bg_image = None
        else: self.bg_image = None

    def _draw_player_panel(self):
        panel_rect = pygame.Rect(20, 20, 220, 150 + (self.num_players * 40))
        draw_glass_rect(self.screen, panel_rect, radius=15)
        
        mode_txt = f"MODE: {self.game_mode} {self.start_score}"
        self.screen.blit(self.font.render(mode_txt, True, CYAN), (35, 30))
        pygame.draw.line(self.screen, GRAY_LIGHT, (30, 60), (230, 60), 1)
        
        for i in range(self.num_players):
            y_pos = 75 + (i * 40)
            is_current = (i == self.current_player_idx)
            color = GREEN if is_current else WHITE
            prefix = "> " if is_current else "   "
            txt = f"{prefix}P{i+1}: {self.scores[i]}"
            self.screen.blit(self.font.render(txt, True, color), (35, y_pos))

    def _handle_throw(self, hit_x, hit_y):
        points = calculate_score(hit_x, hit_y, (self.window_w // 2, self.window_h // 2))
        
        current_score = self.scores[self.current_player_idx]

        if self.game_mode == "LOW":
            new_score = current_score - points
            if new_score < 0:
                self.message = "BUST!"
            elif new_score == 0:
                self.scores[self.current_player_idx] = 0
                self.state = "GAME_OVER"
                self.message = f"GRACZ {self.current_player_idx + 1} WYGRYWA!"
            else:
                self.scores[self.current_player_idx] = new_score
                self.message = f"-{points}"
        else:
            self.scores[self.current_player_idx] += points
            self.message = f"+{points}"
        
        if self.state != "GAME_OVER":
            self.current_player_idx = (self.current_player_idx + 1) % self.num_players

    def _draw_mouse_ui(self):
        cx, cy = self.mouse_aim_pos
        CROSSHAIR_COLOR = (0, 255, 255)
        POWER_COLOR = (255, 50, 50)
        
        if self.mouse_phase == "AIM":
            pygame.draw.circle(self.screen, CROSSHAIR_COLOR, (cx, cy), 10, 2)
            pygame.draw.line(self.screen, CROSSHAIR_COLOR, (cx - 15, cy), (cx + 15, cy), 2)
            pygame.draw.line(self.screen, CROSSHAIR_COLOR, (cx, cy - 15), (cx, cy + 15), 2)
            
        elif self.mouse_phase == "POWER":
            lx, ly = self.mouse_lock_pos
            pygame.draw.circle(self.screen, CROSSHAIR_COLOR, (lx, ly), 10, 2)
            pygame.draw.line(self.screen, CROSSHAIR_COLOR, (lx - 15, ly), (lx + 15, ly), 2)
            pygame.draw.line(self.screen, CROSSHAIR_COLOR, (lx, ly - 15), (lx, ly + 15), 2)
            
            mx, my = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, POWER_COLOR, (lx, ly), (mx, my), 3)
            
            bar_h = 100
            fill_h = int(bar_h * self.current_power)
            rect_bg = pygame.Rect(lx + 30, ly - 50, 20, bar_h)
            rect_fill = pygame.Rect(lx + 30, ly + 50 - fill_h, 20, fill_h)
            
            pygame.draw.rect(self.screen, (50, 50, 50), rect_bg)
            pygame.draw.rect(self.screen, (0, 255, 0) if self.current_power > 0.8 else (255, 255, 0), rect_fill)
            pygame.draw.rect(self.screen, (255, 255, 255), rect_bg, 2)

    def run(self):
        running = True

        overlay_surf = pygame.Surface((self.window_w, self.window_h))
        overlay_surf.set_alpha(150)
        overlay_surf.fill(BLACK)

        while running:
            data = {}

            # Background
            if self.bg_image: self.screen.blit(self.bg_image, (0, 0))
            else: self.screen.fill((30, 30, 35))

            if self.input_method == "Camera":
                frame, data = self.ctrl.process()
                
                # Draw small preview
                if frame is not None:
                    # Draw camera box
                    pygame.draw.rect(self.screen, WHITE, (self.cam_x-2, self.cam_y-2, self.cam_w+4, self.cam_h+4), 2)
                    fr = cv2.resize(frame, (self.cam_w, self.cam_h))
                    fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
                    surf = pygame.surfarray.make_surface(np.swapaxes(fr, 0, 1))
                    self.screen.blit(surf, (self.cam_x, self.cam_y))
                else:
                    pygame.draw.rect(self.screen, BLACK, (self.cam_x, self.cam_y, self.cam_w, self.cam_h))
                    self.screen.blit(self.font.render("NO CAM", True, RED), (self.cam_x+100, self.cam_y+100))

                if self.state == "PLAY":
                    self.bar_left.draw(self.screen, data.get("progress_left", 0))
                    self.bar_right.draw(self.screen, data.get("progress_right", 0))

                    if data.get("aim"):
                        ax, ay = data["aim"]
                        col = NEON_BLUE if data.get("action") != "THROW" else GREEN
                        pygame.draw.circle(self.screen, col, (ax, ay), 15, 2)
                        pygame.draw.line(self.screen, col, (ax-25, ay), (ax+25, ay), 1)
                        pygame.draw.line(self.screen, col, (ax, ay-25), (ax, ay+25), 1)
                
                    action = data.get("action")
                    if action == "PICKUP":
                        self.message = "READY!"
                        self.msg_timer = time.time() + 1.0
                    elif action == "THROW":
                        ax, ay = data["aim"]
                        hit_x = ax + random.randint(-AIM_NOISE, AIM_NOISE)
                        hit_y = ay + random.randint(-AIM_NOISE, AIM_NOISE)
                        self._handle_throw(hit_x, hit_y)
                        self.msg_timer = time.time() + 1.5

                    if time.time() < self.msg_timer:
                        t = self.font_big.render(self.message, True, GOLD)
                        tr = t.get_rect(center=(self.window_w//2, 120))
                        self.screen.blit(t, tr)

            # Draw Game Elements
            self.board.draw(self.screen)
            self._draw_player_panel()

            # Debug mode
            if self.debug:
                self.debug_renderer.draw_calibration_grid(self.board_center)
                self.debug_renderer.draw_confidence_bar(data, self.window_w, self.window_h)
                
                fps = int(self.clock.get_fps())
                fps_col = (0, 255, 0) if fps >= 30 else (255, 0, 0)
                fps_text = self.font.render(f"FPS: {fps}", True, fps_col)
                self.screen.blit(fps_text, (self.window_w - 120, 80))

                if self.state == "PLAY":
                    if "skeleton" in data and data["skeleton"] is not None:
                        self.debug_renderer.draw_skeleton(data)

            # Pause Menu
            elif self.state == "PAUSE":
                self.screen.blit(overlay_surf, (0,0))
                t = self.font_big.render("PAUZA", True, NEON_BLUE)
                self.screen.blit(t, t.get_rect(center=(self.window_w//2, self.window_h//2 - 160)))
                
                self.btn_resume.draw(self.screen)
                self.btn_save.draw(self.screen)
                self.btn_exit.draw(self.screen)

            # Event Handling
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: 
                    if self.ctrl.cap: self.ctrl.cap.release()
                    return "EXIT_APP"
                
                # Debug Toggle
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_d and (ev.mod & pygame.KMOD_CTRL):
                    self.debug = not self.debug
                    print(f"Debug Mode: {self.debug}")

                # Touchpad Logic
                if self.input_method == "Touchpad" and self.state == "PLAY":
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if ev.type == pygame.MOUSEMOTION:
                        if self.mouse_phase == "AIM":
                            self.mouse_aim_pos = mouse_pos
                        elif self.mouse_phase == "POWER":
                            start_y = self.power_drag_start[1]
                            curr_y = mouse_pos[1]
                            dist = max(0, curr_y - start_y)
                            MAX_DRAG = 300.0
                            self.current_power = min(dist / MAX_DRAG, 1.0)

                    elif ev.type == pygame.MOUSEBUTTONDOWN:
                        if ev.button == 1: 
                            if self.mouse_phase == "AIM":
                                self.mouse_phase = "POWER"
                                self.mouse_lock_pos = mouse_pos
                                self.power_drag_start = mouse_pos
                                self.current_power = 0.0

                    elif ev.type == pygame.MOUSEBUTTONUP:
                        if ev.button == 1:
                            if self.mouse_phase == "POWER":
                                target_x, target_y = self.mouse_lock_pos
                                gravity_drop = (1.0 - self.current_power) * 200 
                                final_y = target_y + gravity_drop
                                final_x = target_x 
                                self._handle_throw(int(final_x), int(final_y))
                                self.mouse_phase = "AIM"
                                self.current_power = 0.0

                # UI Interactions
                if self.state == "PLAY":
                    if self.btn_pause_trigger.is_clicked(ev):
                        self.state = "PAUSE"
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        self.state = "PAUSE"
                elif self.state == "PAUSE":
                    if self.btn_resume.is_clicked(ev) or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                        self.state = "PLAY"
                    
                    if self.btn_save.is_clicked(ev):
                        save_data = {
                            "scores": self.scores,
                            "current_player": self.current_player_idx,
                            "game_mode": self.game_mode,
                            "num_players": self.num_players,
                            "start_score": self.start_score,
                            "bg_skin": self.config.get("bg_skin"),
                            "board_skin": self.config.get("board_skin"),
                            "input_method": self.input_method
                        }
                        success = save_game_state(save_data)
                        if success and self.source_filename and success != self.source_filename:
                            delete_save_file(self.source_filename)
                        if self.ctrl.cap: self.ctrl.cap.release()
                        return "BACK_TO_TITLE"
                    
                    if self.btn_exit.is_clicked(ev):
                        if self.ctrl.cap: self.ctrl.cap.release()
                        return "BACK_TO_TITLE"
                    
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: running = False
                    if self.state == "GAME_OVER" and ev.key == pygame.K_RETURN:
                        self.state = "PLAY"
                        initial = self.start_score if self.game_mode == "LOW" else 0
                        self.scores = [initial] * self.num_players
                        self.current_player_idx = 0

            # Drawing Overlays
            if self.state == "PLAY":
                self.btn_pause_trigger.draw(self.screen) 
                if self.input_method == "Touchpad":
                    self._draw_mouse_ui()
                if self.message:
                    color = (255, 50, 50) if "BUST" in self.message else (255, 215, 0)
                    msg_surf = self.font_big.render(self.message, True, color)
                    msg_rect = msg_surf.get_rect(center=(self.window_w // 2, self.window_h - 50))
                    self.screen.blit(msg_surf, msg_rect)

            if self.state == "GAME_OVER":
                self.screen.blit(overlay_surf, (0,0))
                t1 = self.font_big.render("GAME OVER", True, RED)
                t2 = self.font_big.render(self.message, True, GOLD)
                t3 = self.font.render("Press ENTER to restart", True, WHITE)
                cx, cy = self.window_w//2, self.window_h//2
                self.screen.blit(t1, t1.get_rect(center=(cx, cy - 60)))
                self.screen.blit(t2, t2.get_rect(center=(cx, cy + 10)))
                self.screen.blit(t3, t3.get_rect(center=(cx, cy + 80)))

            pygame.display.flip()
            self.clock.tick(FPS)

        self.ctrl.close()
        return "BACK_TO_TITLE"