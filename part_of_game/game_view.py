import pygame

from ui_elements.input_box import InputBox
from ui_elements.text_box import TextBox
from ui_elements.buttom import Buttom

class print_game():#
    def __init__(self,controller):
        pygame.init()
        self.controller=controller
        self.player_x=0
        self.player_y=250
        self.camera_x=0
        self.camera_y=0
        self.camera_width=700
        self.camera_height=700
        self.camera_view = pygame.Rect(self.camera_x, self.camera_y, self.controller.screen_width, self.controller.screen_hight)
        self.in_air=False
        self.err_box = TextBox(200, 400, 300, 40, True)
        self.exit_btn = Buttom(500, 10, 100, 40, True, 'Exit')
        self.key_down=False
        self.last_key = None
        self.solid_color = (0, 0, 0)  # black
        self.map_mask = pygame.mask.from_threshold(self.controller.map_img, self.solid_color, (10, 10, 10))
        self.player_mask = pygame.mask.from_surface(self.controller.player_img)
        self.add_left_right=3
        self.add_up=100
        self.down=False

    def print_map(self):
        self.camera_x = max(0,self.player_x-self.controller.screen_width//2)
        self.camera_view.topleft = (self.camera_x, self.camera_y)
        self.camera_view = pygame.Rect(self.camera_x, self.camera_y, self.controller.screen_width, self.controller.screen_hight)
        self.controller.screen.blit(self.controller.map_img, (0, 0),self.camera_view)
        self.controller.screen.blit(self.controller.player_img, (self.player_x-self.camera_x, self.player_y-self.camera_y))
        self.exit_btn.draw(self.controller.screen)
        pygame.display.flip()

    def game(self):
        while not self.controller.finish:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.controller.finish = True

                if event.type==pygame.KEYUP:
                    #print('key up')
                    self.key_down=False

                if event.type == pygame.KEYDOWN or self.key_down:
                    if self.key_down:
                        if self.last_key==pygame.K_d:
                            if not self.col(self.player_x+self.add_left_right, self.player_y):
                                self.player_x+=self.add_left_right
                                print('going right')
                            else:
                                self.go_over_x(1)
                        if self.last_key==pygame.K_a:
                            if self.player_x>0:
                                if not self.col(self.player_x-self.add_left_right, self.player_y):
                                    self.player_x-=self.add_left_right
                                    print('going left')
                                else:
                                    self.go_over_x(-1)
                        if self.last_key==pygame.K_w:
                            if not self.col(self.player_x, self.player_y-self.add_up) and not self.in_air:
                                self.player_y -= self.add_up
                                self.camera_y -= self.add_up
                                self.in_air = True
                        if self.last_key==pygame.K_s:
                            if not self.col(self.player_x, self.player_y+10):
                                self.player_y += 10
                                self.camera_y += 10
                    else:

                        if event.key==pygame.K_d:
                            print('here',self.col(self.player_x+self.add_left_right,self.player_y))
                            if not self.col(self.player_x+self.add_left_right,self.player_y):
                                self.player_x+=self.add_left_right
                                self.last_key=event.key
                                print('going right')
                            else:
                                self.go_over_x(1)
                        if event.key==pygame.K_a:
                            self.last_key = event.key
                            if self.player_x>0:
                                if not self.col(self.player_x - self.add_left_right, self.player_y):
                                    self.player_x-=self.add_left_right
                                    print('going left')
                                else:
                                    self.go_over_x(-1)
                        if event.key==pygame.K_w:
                            if not self.col(self.player_x, self.player_y-self.add_up) and not self.in_air:
                                self.last_key = event.key
                                self.player_y -= self.add_up
                                self.camera_y -= self.add_up
                                self.in_air=True
                                print('going up')
                        if event.key == pygame.K_s:
                            if not self.col(self.player_x, self.player_y+10):
                                self.last_key = event.key
                                self.player_y += 10
                                self.camera_y += 10
                                print('going down')
                    self.key_down = True

                if event.type==pygame.MOUSEBUTTONDOWN:
                    if self.exit_btn.is_clicked(event.pos):
                        print('exiting')
                        self.controller.exit()
                        break
                    else:
                        print(event.pos)
            if self.in_air:
                if not self.col(self.player_x, self.player_y+1):
                    self.player_y+=10
                    self.camera_y+=10
                elif not self.go_down():
                    self.in_air=False
            else:
                if not self.col(self.player_x, self.player_y+1):
                    self.player_y+=10
                    self.camera_y +=10
                    self.down=True
                elif self.down:
                    pass
                    self.down=self.go_down()


            if not self.controller.finish:
                self.print_map()

                pygame.display.flip()
                self.controller.clock.tick(30)
        print('stop2')
    def col(self,x,y):
        if self.map_mask.overlap(self.player_mask, (x, y)):
            #print('true')
            return True
        #print('False')
        return False

    def go_over_x(self,r_l,steps=15):#r_l is right or left if it is left it will be -1
        for i in range(1,steps):
            if not self.col(self.player_x+(self.add_left_right*r_l),self.player_y-i):
                self.player_y-=i
                self.camera_y-=i
                self.player_x+=(self.add_left_right*r_l)
                self.camera_x+=(self.add_left_right*r_l)
                print('ok')
                break
        print('not ok')
    def go_down(self,steps=10):
        for i in range(1,steps):
            if not self.col(self.player_x,self.player_y+i):
                self.player_y+=i
                self.camera_y+=i
                return True
        return False