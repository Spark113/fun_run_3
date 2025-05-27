import pygame

class TextBox:
    def __init__(self, x, y, w, h,to_draw=True, placeholder='errs and updats here'):
        pygame.init()
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.txt_surf = pygame.font.Font(None, 32).render(placeholder, True, pygame.Color('black'))
        self.d_text=placeholder
        self.to_draw=to_draw

    def set_text(self,text):
        self.d_text=text
        self.txt_surf = pygame.font.Font(None, 32).render(self.d_text, True, pygame.Color('black'))

    def set_to_draw(self,to_draw):
        self.to_draw=to_draw

    def draw(self,screen):
        if self.to_draw:
            screen.blit(self.txt_surf, (self.rect.x + 5, self.rect.y + 5))
            # Draw rect
            pygame.draw.rect(screen, self.color, self.rect, 2)
