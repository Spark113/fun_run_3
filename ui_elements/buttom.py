import pygame

class Buttom():
    def __init__(self, x, y, w, h,to_draw, text):
        pygame.init()
        self.rect = pygame.Rect(x, y, w, h)
        self.text_surf = pygame.font.Font(None, 32).render(text, True, pygame.Color('white'))
        self.to_draw = to_draw
        self.text=text


    def set_to_draw(self,to_draw):
        self.to_draw=to_draw

    def draw(self, screen):
        if self.to_draw:
            pygame.draw.rect(screen, pygame.Color('gray20'), self.rect)
            screen.blit(self.text_surf, (self.rect.x + (self.rect.w - self.text_surf.get_width()) // 2,self.rect.y + (self.rect.h - self.text_surf.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
