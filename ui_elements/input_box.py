import pygame

class InputBox:
    def __init__(self, x, y, w, h,to_draw=True,hide=False, placeholder=''):
        pygame.init()
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active   = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text  = placeholder
        self.txt_surf = pygame.font.Font(None, 32).render(placeholder, True, pygame.Color('black'))
        self.active = False
        self.hide=hide
        self.display_text=''
        self.to_draw=to_draw


    def set_to_draw(self,to_draw):
        self.to_draw=to_draw

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state if clicked in box
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
            if self.active:
                self.text = ''
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Limit input length if you like
                self.text += event.unicode
            # Render text (hide for password if you want)

            if self.hide:
                self.display_text='*'*len(self.text)
            else:
                self.display_text =self.text
            self.txt_surf = pygame.font.Font(None, 32).render(self.display_text, True, pygame.Color('black'))


    def draw(self, screen):
        if self.to_draw:
            # Blit text
            screen.blit(self.txt_surf, (self.rect.x + 5, self.rect.y + 5))
            # Draw rect
            pygame.draw.rect(screen, self.color, self.rect, 2)
