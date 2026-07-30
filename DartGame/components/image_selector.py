import pygame
import os
from config.consts import *
from components.ui_utils import draw_glass_rect

class ImageSelector:
    def __init__(self, x, y, w, h, label, options, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.options = options
        self.font = font
        self.idx = 0
        
        padding = 10
        btn_size = 40
        
        self.arrow_l_rect = pygame.Rect(self.rect.left + padding, 
                                        self.rect.centery - btn_size//2, 
                                        btn_size, btn_size)
                                        
        self.arrow_r_rect = pygame.Rect(self.rect.right - padding - btn_size,
                                        self.rect.centery - btn_size//2,
                                        btn_size, btn_size)
        
        #Image
        img_x = self.arrow_l_rect.right + padding
        img_w = self.arrow_r_rect.left - img_x - padding
        self.image_area = pygame.Rect(img_x, self.rect.top + 40, img_w, self.rect.height - 50)
        
        self.current_image = None
        self._load_image()

    def _load_image(self):
        path = self.options[self.idx]
        if not path or not os.path.exists(path):
            self.current_image = None
            return

        try:
            img = pygame.image.load(path).convert_alpha()
            
            #Scale to fit in box
            iw, ih = img.get_size()
            scale = min(self.image_area.width / iw, self.image_area.height / ih)
            new_w, new_h = int(iw * scale), int(ih * scale)
            self.current_image = pygame.transform.smoothscale(img, (new_w, new_h))
        except:
            self.current_image = None

    def get_selected(self):
        return self.options[self.idx]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.arrow_l_rect.collidepoint(event.pos):
                self.idx = (self.idx - 1) % len(self.options)
                self._load_image()
            elif self.arrow_r_rect.collidepoint(event.pos):
                self.idx = (self.idx + 1) % len(self.options)
                self._load_image()

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        # Label
        lbl = self.font.render(self.label, True, NEON_BLUE)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()//2, self.rect.y - 35))

        # Box
        draw_glass_rect(surface, self.rect, radius=20)

        # Image
        if self.current_image:
            img_rect = self.current_image.get_rect(center=self.image_area.center)
            surface.blit(self.current_image, img_rect)
        else:
            txt = self.font.render("No Image", True, (150, 150, 150))
            surface.blit(txt, txt.get_rect(center=self.image_area.center))

        # Arrows
        hover_l = self.arrow_l_rect.collidepoint(mouse_pos)
        hover_r = self.arrow_r_rect.collidepoint(mouse_pos)

        draw_glass_rect(surface, self.arrow_l_rect, radius=10, is_hovered=hover_l)
        draw_glass_rect(surface, self.arrow_r_rect, radius=10, is_hovered=hover_r)
        
        tl = self.font.render("<", True, WHITE)
        tr = self.font.render(">", True, WHITE)
        surface.blit(tl, tl.get_rect(center=self.arrow_l_rect.center))
        surface.blit(tr, tr.get_rect(center=self.arrow_r_rect.center))