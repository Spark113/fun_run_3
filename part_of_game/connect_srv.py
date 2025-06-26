import pygame
from ui_elements.input_box import InputBox
from ui_elements.text_box import TextBox
from ui_elements.buttom import Buttom

class connect():#
    def __init__(self,controller):
        pygame.init()
        self.controller=controller
        self.server_ip = InputBox(200, 200, 300, 40, True, placeholder='127.0.0.1')
        self.server_port = InputBox(200, 260, 300, 40, True, placeholder='3001')
        self.connect_btn = Buttom(300, 330, 100, 40, True, 'Connect')
        self.exit_btn = Buttom(300, 460, 100, 40, True, 'Exit')
        #self.conected=False

    def attempt_connect(self,server_ip,server_port):
        try:
            self.controller.sock.connect((server_ip, int(server_port)))
            self.controller.sock.settimeout(1)
            self.controller.conected = True
            self.controller.err_box.set_text('conected')
            self.controller.listener.start()
        except Exception as err:
            print(err)
            self.controller.conected = False
            self.controller.err_box.set_text('could not connect')
            self.draw_all()

    def connect_to_srv(self):
        if self.controller.debug:
            print('finish',self.controller.finish)
        while not self.controller.finish and not self.controller.conected:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.controller.finish = True
                self.server_ip.handle_event(event)
                self.server_port.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.connect_btn.is_clicked(event.pos):
                        if self.controller.debug:
                            print("Attempting connect with:", self.server_ip.text, self.server_port.text)
                        self.attempt_connect(self.server_ip.text, self.server_port.text)
                        if self.controller.debug:
                            print('connected: ',self.controller.conected)
                    if self.exit_btn.is_clicked(event.pos):
                        print('exiting')
                        self.controller.exit()
                        break
            if not self.controller.finish:
                self.draw_all()
    def draw_all(self):
        self.controller.screen.blit(self.controller.img_start, (0, 0))
        self.server_ip.draw(self.controller.screen)
        self.server_port.draw(self.controller.screen)
        self.connect_btn.draw(self.controller.screen)
        self.exit_btn.draw(self.controller.screen)
        self.controller.err_box.draw(self.controller.screen)
        pygame.display.flip()