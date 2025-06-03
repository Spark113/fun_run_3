import pygame
from ui_elements.input_box import InputBox
from ui_elements.text_box import TextBox
from ui_elements.buttom import Buttom

from encrption.tcp_by_size import send_with_size,recv_by_size


class room():
    def __init__(self, controller):
        pygame.init()
        self.controller = controller
        self.refresh_btn = Buttom(100, 500, 150, 40, True, 'refresh')
        self.make_room_btn = Buttom(500, 500, 150, 40, True, 'make room')
        self.room_id = InputBox(450, 550, 240, 40, True, placeholder='room name')
        self.exit_btn = Buttom(300, 460, 100, 40, True, 'Exit')
        self.rooms_lst=[]
        self.joined=False

    def make_lst(self,data):
        start_x = 100
        start_y = 50
        print(data,'in r')
        cnt=0
        for k,v in data.items():
            print(v,'in i')
            print(k)
            #for k,v in i:
            self.rooms_lst.append(Buttom(start_x, start_y + (cnt * 40), 400, 40, True,f'room name:{k}, players in {v}'))
            cnt += 1

    def show_rooms(self):
        print('start')
        send_with_size(self.controller.sock, ('GRS~').encode())
        while not self.controller.finish and not self.joined:
            for event in pygame.event.get():

                self.room_id.handle_event(event)

                if event.type == pygame.QUIT:
                    self.controller.finish = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.make_room_btn.is_clicked(event.pos):
                        send_with_size(self.controller.sock, (f'MRS~{self.room_id.text}').encode())
                    if self.refresh_btn.is_clicked(event.pos):
                        send_with_size(self.controller.sock, ('GRS~').encode())
                    if self.exit_btn.is_clicked(event.pos):
                        print('exiting')
                        self.controller.exit()
                        break
                    for i in self.rooms_lst:
                        if i.is_clicked(event.pos):
                            print(i.text)
                            room_id=i.text.split(',')[0]
                            room_id=room_id.split(':')[1]
                            print(room_id)#i tested it is working
                            send_with_size(self.controller.sock, (f'JRI~{room_id}').encode())#join room id
            if not self.controller.finish:
                self.draw_all()
                pygame.display.flip()
                self.controller.clock.tick(self.controller.refresh)

    def draw_all(self):
        self.controller.screen.blit(self.controller.img_start, (0, 0))
        self.refresh_btn.draw(self.controller.screen)
        self.make_room_btn.draw(self.controller.screen)
        self.room_id.draw(self.controller.screen)
        self.exit_btn.draw(self.controller.screen)
        self.controller.err_box.draw(self.controller.screen)
        start_x=300
        start_y = 50
        for i in self.rooms_lst:
            i.draw(self.controller.screen)

        pygame.display.flip()

