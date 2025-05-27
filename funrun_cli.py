import pickle
import os

from Demos.desktopmanager import hicon
from requests.utils import dotted_netmask

from encrption.RSA import RSA_CLASS
from encrption.tcp_by_size import send_with_size, recv_by_size
from encrption.TCP_AES import Encrypt_AES
import threading
import base64
import socket
import pygame

from ui_elements.input_box import InputBox
from ui_elements.text_box import TextBox
from ui_elements.buttom import Buttom
from part_of_game.connect_srv import connect
from part_of_game.login import log
from part_of_game.rooms import room
class Game():
    def __init__(self):
        self.debug=True
        self.conected=False
        self.sock=socket.socket()
        self.listener = threading.Thread(target=self.listen)
        self.finish=False
        self.finish_login=False
        self.rsa_object=RSA_CLASS()
        self.server_key=None
        self.connect_obj=connect(self)
        self.login_obj=log(self)
        self.rooms_obj=room(self)
        """py game"""
        self.window_width=700
        self.window_hight=700
        pygame.init()
        pygame.mouse.set_visible(True)
        self.screen=pygame.display.set_mode((self.window_width,self.window_hight))
        pygame.display.set_caption('fun run game')
        self.img_start=pygame.image.load('start.png').convert()
        self.screen.blit(self.img_start,(0,0))
        self.clock=pygame.time.Clock()
        self.refresh=60

        self.refresh_btn=Buttom(100, 500, 150, 40,False, 'refresh')
        self.make_room_btn=Buttom(500, 500, 150, 40,False, 'make room')
        self.room_id=InputBox(450, 550, 240, 40,False, placeholder='room name')

        self.err_box=TextBox(200,400,300,40,True)
        self.exit_btn=Buttom(300, 460, 100, 40,True, 'exit')

        self.connect_obj.connect_to_srv()

        self.login_obj.login_loop()

        self.rooms_obj.show_rooms()
        print('done')#works now i need to do the game
        pygame.quit()

    def main_game(self):
        while True:
            print('hi')
        pass


    def exit(self):
        try:
            self.err_box.set_text('shoting down')
            self.draw_all()
            self.finish = True
            if self.conected:
                self.listener.join()
                send_with_size(self.sock, b'BYE')
                self.sock.close()
            pygame.quit()

        except Exception as err:
            if self.debug:
                print('--------------------------------------------------')
                print(err)
                print('--------------------------------------------------')


    #need to check that all the thing are in here
    def draw_all(self):
        self.screen.blit(self.img_start, (0, 0))  # to clear the screen

        self.refresh_btn.draw(self.screen)
        self.make_room_btn.draw(self.screen)
        self.room_id.draw(self.screen)

        self.err_box.draw(self.screen)
        self.exit_btn.draw(self.screen)
        pygame.display.flip()

    def listen(self):
        while not self.finish:
            try:
                data = recv_by_size(self.sock)
                if data==b'':
                    print('server disconnected')
                    break
                if data.startswith(b'GRS~'):
                    action = data[:3]
                    fields = data[4:]
                    print(fields)
                    d=pickle.loads(fields)
                    print(d)
                    self.rooms_obj.make_lst(d)
                    self.rooms_obj.err_box.set_text('get refresh')
                    self.draw_all()
                else:
                    data=data.decode()
                    action = data[:3]
                    fields = data[4:].split('~')
                    if action == 'LOG':
                        if fields[0]=='Login Successful':
                            self.finish_login=True
                            self.err_box.set_text(fields[0])
                            self.draw_all()
                        else:
                            self.login_obj.err_box.set_text(fields[0])
                            self.draw_all()

                    if action=='SUP':
                        self.err_box.set_text(fields[0])
                        self.draw_all()

                    if action=='FRS':
                        try:
                            rsa_encrypted_key = base64.b64decode(fields[0])
                            key = self.rsa_object.decrypt_RSA(rsa_encrypted_key)
                            if self.debug:
                                print('--------------------------------------------------')
                                print(f'key= {key}')
                                print(len(key))
                                print('--------------------------------------------------')
                            self.server_key = key
                        except Exception as err:
                            if self.debug:
                                print('--------------------------------------------------')
                                print(err)
                                print('--------------------------------------------------')

                    if action=='MRS':
                        self.rooms_obj.err_box.set_text(fields[0])
                        #self.draw_all()
                    if action=='GRS':
                        self.rooms_obj.make_lst(pickle.loads(fields[0].encode()))
                        self.rooms_obj.err_box.set_text('get refresh')
                        #self.draw_all()
                    if action == 'JRI':
                        self.rooms_obj.err_box.set_text(fields[0])
                        self.rooms_obj.joined=True
                        #self.draw_all()
                    if action=='ERR':
                        self.err_box.set_text(fields[0])
                        self.draw_all()
            except socket.timeout:
                continue
            except Exception as e:
                print("Listener encountered error:", e)
                self.err_box.set_text(e)
                self.draw_all()
                break


if __name__=='__main__':
    a=Game()