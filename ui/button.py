import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color, text_color, action_value=None, border_radius=12, is_secondary=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = color
        self.current_color = color
        self.text_color = text_color
        self.action_value = action_value
        self.border_radius = border_radius
        self.is_secondary = is_secondary
        self.is_hovered = False
        
        self._update_text_surface()

    def _update_text_surface(self):
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        
        if self.text_rect.width > self.rect.width - 20:
            scale = (self.rect.width - 20) / self.text_rect.width
            new_size = int(self.font.get_height() * scale)
            temp_font = pygame.font.SysFont("Verdana", new_size)
            self.text_surface = temp_font.render(self.text, True, self.text_color)
            self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        # Shadow effect
        shadow_rect = self.rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(surface, (15, 15, 20), shadow_rect, border_radius=self.border_radius)
        
        draw_color = self.current_color
        if self.is_hovered:
            # Lighten for hover
            draw_color = tuple(min(c + 25, 255) for c in draw_color)
            
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=self.border_radius)
        
        # Border for depth
        border_color = (255, 255, 255, 50) if not self.is_secondary else (200, 200, 255, 30)
        pygame.draw.rect(surface, border_color, self.rect, width=1 if self.is_secondary else 2, border_radius=self.border_radius)
        
        surface.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return self.action_value
        return None
