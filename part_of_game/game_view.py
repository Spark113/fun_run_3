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
        self.saw_blade_mask=pygame.mask.from_surface(self.controller.saw_blade_img)
        #self.saw_blade=controller.saw_blade_img
        self.obsticle=False
        self.obsticle_x=0
        self.obsticle_y=0
        self.add_obsticle=15
        self.add_left_right=3
        self.add_up=30
        self.down=False
        self.players={}
        self.obsticles={}
        self.cant_move = False

    def print_map(self):

        self.camera_x = max(0,self.player_x-self.controller.screen_width//2)
        self.camera_view.topleft = (self.camera_x, self.camera_y)
        self.camera_view = pygame.Rect(self.camera_x, self.camera_y, self.controller.screen_width, self.controller.screen_hight)
        self.controller.screen.blit(self.controller.map_img, (0, 0),self.camera_view)
        self.controller.screen.blit(self.controller.player_img, (self.player_x-self.camera_x, self.player_y-self.camera_y))
        for k,v in self.players.items():
            self.controller.screen.blit(self.controller.player_img,(int(v[0]) - self.camera_x,int(v[1]) - self.camera_y))
        for k,v in self.obsticles.items():
            #print('playrs', self.players)
            #print('obsticles', self.obsticles)
            if int(v[0]) !=0 and int(v[1])!=0:
                self.controller.screen.blit(self.controller.saw_blade_img,(int(v[0])-self.camera_x, int(v[1])-self.camera_y))
        if self.obsticle_x!=0 and self.obsticle_y!=0:
            self.controller.screen.blit(self.controller.saw_blade_img, (self.obsticle_x - self.camera_x, self.obsticle_y - self.camera_y))
        self.exit_btn.draw(self.controller.screen)
        pygame.display.flip()

    def game(self):
        max_x=10
        max_y=10
        val_x=0
        val_y=1
        #obsticle_val_x=0
        #obsticle_val_y=0
        moved=False
        obsticle_cnt=45
        cant_move_cnt=100
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
                        self.in_air = True
                if key[pygame.K_o]:
                    if obsticle_cnt>0:
                        self.obsticle=True
                        self.obsticle_x=self.player_x+self.add_obsticle
                        self.obsticle_y=self.player_y
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if self.exit_btn.is_clicked(event.pos):
                        print('exiting')
                        self.controller.exit()
                        break
                    else:
                        print(event.pos)
            if not self.cant_move:
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
                else:
                    self.in_air=False
                if not self.col(self.player_x+val_x, self.player_y):
                    self.player_x +=val_x
                    if val_x!=0:
                        moved = True
                else:
                    if self.go_over_x(val_x):
                        moved = True

                if moved:
                    send_with_size(self.controller.sock, (f'UPD~{str(self.player_x)}~{str(self.player_y)}').encode())
                    moved=False

            else:
                cant_move_cnt-=1
                if cant_move_cnt==0:
                    self.cant_move=False
            """from here its obsticle movment"""
            if self.obsticle_x !=0 and self.obsticle_y!=0:
                obsticle_cnt-=1
                o_moved=False
                if not self.col(self.obsticle_x+self.add_obsticle,self.obsticle_y):
                    self.obsticle_x+=self.add_obsticle
                    o_moved=True
                else:
                    for i in range(1,20):
                        if not self.col(self.obsticle_x+1,self.obsticle_y-1):
                            self.obsticle_y -= i
                            self.obsticle_x += 1
                            obsticle_cnt+=1
                            break
                if not self.col(self.obsticle_x,self.obsticle_y+10):
                    self.obsticle_y+=10
                    o_moved = True
                if o_moved:
                    send_with_size(self.controller.sock, (f'UPO~{str(self.obsticle_x)}~{str(self.obsticle_y)}').encode())
                    o_moved=False
            if obsticle_cnt==0:
                obsticle_cnt=45
                self.obsticle_x=0
                self.obsticle_y=0
                send_with_size(self.controller.sock, (f'UPO~{str(self.obsticle_x)}~{str(self.obsticle_y)}').encode())
            if self.col_obsticle():
                print('col')
                self.cant_move=True
            if not self.controller.finish:
                self.print_map()

                pygame.display.flip()
                self.controller.clock.tick(30)
        print('stop2')
    def col(self,x,y):
        if self.map_mask.overlap(self.player_mask, (x, y)):
            return True
        return False

    def col_obsticle(self):
        player_w, player_h = self.controller.player_img.get_size()
        blade_w, blade_h = self.controller.saw_blade_img.get_size()
        player_rect = pygame.Rect(self.player_x, self.player_y, player_w, player_h)
        for k,v in self.obsticles.items():
            if int(v[0]) !=0 and int(v[1])!=0:
                blade_rect = pygame.Rect(int(v[0]),int(v[1]), blade_w, blade_h)
                if player_rect.colliderect(blade_rect):
                    return True

    def go_over_x(self,val_x,steps=15):
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