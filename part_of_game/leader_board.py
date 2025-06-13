import pygame

from ui_elements.input_box import InputBox
from ui_elements.text_box import TextBox
from ui_elements.buttom import Buttom
import time
from encrption.tcp_by_size import send_with_size,recv_by_size
class board():
    def __init__(self,controller):
        self.controller=controller
        self.wating_for_playrs=TextBox(250,300,300,40,True,'wating for players...')
        self.board_lst=[]
        self.board_ready=False
        self.exit_btn = Buttom(300, 460, 100, 40, True, 'Exit')
    def board_draw(self):
        cnt=0
        while not self.controller.finish:
            for event in pygame.event.get():
                time.sleep(0.5)
                self.wating_for_playrs.set_text('wating for players' + (cnt * '.'))
                cnt += 1
                cnt = cnt % 5
                if event.type == pygame.QUIT:
                    self.controller.finish = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.exit_btn.is_clicked(event.pos):
                        print('exiting')
                        self.controller.exit()
                        break
            if not self.controller.finish:
                self.draw_all()
                pygame.display.flip()
                self.controller.clock.tick(self.controller.refresh)

    def dict_to_lst(self,dict):
        start_x = 100
        start_y = 50
        cnt = 0
        #self.board_lst=[]
        for k,v in dict.items():
            self.board_lst.append(TextBox(start_x,start_y+ (cnt * 40),300,40,True,str(k)+' time: '+str(v)))

    def draw_all(self):
        self.controller.screen.blit(self.controller.img_start, (0, 0))

        self.exit_btn.draw(self.controller.screen)
        self.controller.err_box.draw(self.controller.screen)
        if self.board_ready:
            for i in self.board_lst:
                i.draw(self.controller.screen)
        else:
            self.wating_for_playrs.draw(self.controller.screen)

        pygame.display.flip()