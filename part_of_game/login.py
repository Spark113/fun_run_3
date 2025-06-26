import pygame
from ui_elements.input_box import InputBox
from ui_elements.text_box import TextBox
from ui_elements.buttom import Buttom
import base64
from encrption.tcp_by_size import send_with_size,recv_by_size
from encrption.TCP_AES import Encrypt_AES,Decrypt_AES
import os

class log():
    def __init__(self, controller):#
        pygame.init()
        self.controller = controller
        self.user_box = InputBox(200, 200, 300, 40, True, placeholder='Username')
        self.pass_box = InputBox(200, 260, 300, 40, True, True, placeholder='Password')
        self.login_btn = Buttom(240, 330, 100, 40, True, 'Login')
        self.sign_up_btn = Buttom(360, 330, 100, 40, True, 'sign up')
        self.exit_btn = Buttom(300, 460, 100, 40, True, 'Exit')

    def attemp_login(self,username,paswword):
        if self.controller.server_key==None:
            public_key = self.controller.rsa_object.public_key
            public_key_b64 = base64.b64encode(public_key).decode()
            if self.controller.debug:
                print('--------------------------------------------------')
                print('public_key=', public_key)
                print('--------------------------------------------------')
            msg = f'GSR~{public_key_b64}'
            send_with_size(self.controller.sock, msg.encode())
            while self.controller.server_key==None:
                continue
            if self.controller.debug:
                print('--------------------------------------------------')
                print('srv key= ' + str(self.controller.server_key))
                print('--------------------------------------------------')
        iv = os.urandom(16)
        user_name1 = Encrypt_AES(f'{username}', self.controller.server_key, iv)
        user_name = base64.b64encode(user_name1).decode()
        password = Encrypt_AES(f'{paswword}', self.controller.server_key, iv)
        password = base64.b64encode(password).decode()
        iv = base64.b64encode(iv).decode()
        login_str = f'LGN~{user_name}~{password}~{iv}'
        send_with_size(self.controller.sock,login_str.encode())


    def login_loop(self):
        while not self.controller.finish and not self.controller.finish_login:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.controller.finish = True
                self.user_box.handle_event(event)
                self.pass_box.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.login_btn.is_clicked(event.pos):
                        if self.controller.debug:
                            print("Attempting login with:", self.user_box.text, self.pass_box.text)
                        self.attemp_login(self.user_box.text, self.pass_box.text)
                    if self.sign_up_btn.is_clicked(event.pos):
                        if self.controller.debug:
                            print("Attempting login with:", self.user_box.text, self.pass_box.text)
                        send_with_size(self.controller.sock, (f'SGU~{self.user_box.text}~{self.pass_box.text}').encode())

                    if self.exit_btn.is_clicked(event.pos):
                        print('exiting')
                        self.controller.exit()
                        break

            if not self.controller.finish:
                self.draw_all()

                pygame.display.flip()
                self.controller.clock.tick(30)

    def draw_all(self):
        self.controller.screen.blit(self.controller.img_start, (0, 0))
        self.user_box.draw(self.controller.screen)
        self.pass_box.draw(self.controller.screen)
        self.login_btn.draw(self.controller.screen)
        self.exit_btn.draw(self.controller.screen)
        self.controller.err_box.draw(self.controller.screen)
        self.sign_up_btn.draw(self.controller.screen)
        pygame.display.flip()
