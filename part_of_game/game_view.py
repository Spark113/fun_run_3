import pygame

from ui_elements.input_box import InputBox
from ui_elements.text_box import TextBox
from ui_elements.buttom import Buttom
from encrption.tcp_by_size import send_with_size,recv_by_size

class print_game():#
    def __init__(self,controller):
        pygame.init()
        self.controller=controller
        self.player_x=0
        self.player_y=420
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
        self.map_mask = pygame.mask.from_threshold(self.controller.mask_map_img, (255, 255, 255), (1, 1, 1))
        self.white_mask = pygame.mask.from_threshold(self.controller.mask_map_img, (255, 255, 255), (1, 1, 1))#get the withe part
        self.map_mask = self.white_mask.copy()
        self.map_mask.invert()#get every thing except the white part
        self.player_mask = pygame.mask.from_surface(self.controller.player_img)
        self.add_left_right=3
        self.add_up=30
        self.down=False
        self.players={}

    def print_map(self):
        self.camera_x = max(0,self.player_x-self.controller.screen_width//2)
        self.camera_view.topleft = (self.camera_x, self.camera_y)
        self.camera_view = pygame.Rect(self.camera_x, self.camera_y, self.controller.screen_width, self.controller.screen_hight)
        self.controller.screen.blit(self.controller.map_img, (0, 0),self.camera_view)
        self.controller.screen.blit(self.controller.player_img, (self.player_x-self.camera_x, self.player_y-self.camera_y))
        for k,v in self.players.items():
            self.controller.screen.blit(self.controller.player_img,(int(v[0]) - self.camera_x,int(v[1]) - self.camera_y))
        self.exit_btn.draw(self.controller.screen)
        pygame.display.flip()

    def game(self):
        max_x=10
        max_y=10
        val_x=0
        val_y=1
        moved=False
        while not self.controller.finish:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.controller.finish = True
                key=pygame.key.get_pressed()
                if key[pygame.K_d]:
                    if not self.col(self.player_x + self.add_left_right, self.player_y):
                        if val_x<max_x:
                            val_x+=self.add_left_right
                    else:
                        self.go_over_x(1)
                if key[pygame.K_a]:
                    if self.player_x > 0:
                        if not self.col(self.player_x - self.add_left_right, self.player_y):
                            if val_x > (max_x*-1):
                                val_x -= self.add_left_right
                        else:
                            self.go_over_x(-1)
                if key[pygame.K_w]:
                    if not self.col(self.player_x, self.player_y - self.add_up) and not self.in_air:
                        val_y-= self.add_up
                        print('here',val_y)
                        self.in_air = True

                if event.type==pygame.MOUSEBUTTONDOWN:
                    if self.exit_btn.is_clicked(event.pos):
                        print('exiting')
                        self.controller.exit()
                        break
                    else:
                        print(event.pos)
            if val_y!=10:
                val_y+=1
            if val_x!=0:
                if not self.in_air:
                    if val_x>0:
                        val_x-=1
                    else:
                        val_x+=1
                else:
                    if val_x>0:
                        val_x=5
                    else:
                        val_x=-5
            if not self.col(self.player_x, self.player_y+val_y):
                self.player_y +=val_y
                self.camera_y +=val_y
                moved=True
                #print(self.col(self.player_x, self.player_y+val_y),'in y')
            else:
                self.in_air=False
                #print(self.col(self.player_x, self.player_y + val_y), 'in y')
            if not self.col(self.player_x+val_x, self.player_y):
                self.player_x +=val_x
                if val_x!=0:
                    moved = True
                #print(self.col(self.player_x+val_x, self.player_y),'in x')
            else:
                if self.go_over_x(val_x):
                    moved = True
                    #print(self.go_over_x(val_x),'going down')
            #print(moved,'moved')
            if moved:#(self.player_x-self.camera_x, self.player_y-self.camera_y)
                send_with_size(self.controller.sock, (f'UPD~{str(self.player_x)}~{str(self.player_y)}').encode())
                moved=False
                #print(moved,'moved')
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

    def go_over_x(self,val_x,steps=15):#r_l is right or left if it is left it will be -1
        for i in range(1,steps):
            if not self.col(self.player_x+val_x,self.player_y-i):
                self.player_y-=i
                self.camera_y-=i
                self.player_x+=val_x
                self.camera_x+=val_x
                return True
        return False
    def go_down(self,steps=10):
        for i in range(1,steps):
            if not self.col(self.player_x,self.player_y+i):
                self.player_y+=i
                self.camera_y+=i
                return True
        return False