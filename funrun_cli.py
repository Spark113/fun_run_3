import pickle
import os
from multiprocessing.reduction import duplicate

from pandas.core.algorithms import duplicated

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
from part_of_game.game_view import print_game
class Game():
    def __init__(self):
        """py game"""#
        self.screen_width = 700
        self.screen_hight = 700
        pygame.init()
        pygame.mouse.set_visible(True)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_hight))

        self.err_box = TextBox(200, 400, 300, 40, True)

        pygame.display.set_caption('fun run game')
        self.img_start = pygame.image.load('start.png').convert()
        self.player_img = pygame.image.load('among_us.png').convert_alpha()
        self.map_img = pygame.image.load('map2.png').convert()
        #self.map_img = pygame.image.load('mask_map.png').convert()
        self.mask_map_img=pygame.image.load('mask_map.png').convert()
        self.speed_musk_img=pygame.image.load('speed_musk.png').convert()
        self.saw_blade_img=pygame.image.load('saw_blade2.png').convert_alpha()
        self.screen.blit(self.img_start, (0, 0))
        self.clock = pygame.time.Clock()
        self.refresh = 60

        """משתנים של הלקוח"""
        self.debug=True
        self.conected=False
        self.sock=socket.socket()
        self.listener = threading.Thread(target=self.listen)
        self.finish=False
        self.can_close=True
        self.finish_login=False
        self.rsa_object=RSA_CLASS()
        self.server_key=None
        self.connect_obj=connect(self)
        self.login_obj=log(self)
        self.rooms_obj=room(self)
        self.run_game=print_game(self)
        print('start')
        if not self.finish:
            self.connect_obj.connect_to_srv()
        if not self.finish:
            self.login_obj.login_loop()
        self.can_close = False
        if not self.finish:
            self.rooms_obj.show_rooms()
        if not self.finish:
            self.run_game.game()
        print('done')#works now i need to do the game
        pygame.quit()

    def main_game(self):
        while True:
            print('hi')
        pass


    def exit(self):
        try:
            self.err_box.set_text('shoting down')
            self.finish = True
            if self.conected:
                send_with_size(self.sock, b'BYE')
                while not self.can_close:
                    continue
                self.listener.join()
                self.sock.close()
            pygame.quit()
            print('got out')
        except Exception as err:
            if self.debug:
                print('--------------------------------------------------')
                print(err)
                print('--------------------------------------------------')




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
                    self.err_box.set_text('get refresh')
                elif data.startswith(b'GOP~'):
                    action = data[:3]
                    fields = data[4:]
                    d = pickle.loads(fields)
                    o={}
                    for k,v in d.items():
                        o[k]=(0,0)
                    print('o',o)
                    print('d', d)
                    self.run_game.players=d
                    self.run_game.obsticles=o
                else:
                    data=data.decode()
                    action = data[:3]
                    fields = data[4:].split('~')
                    if action == 'LOG':
                        if fields[0]=='Login Successful':
                            self.finish_login=True
                            self.err_box.set_text(fields[0])
                        else:
                            self.err_box.set_text(fields[0])

                    elif action=='UPP':
                        self.run_game.players[fields[2]]=((fields[0],fields[1]))
                    elif action=='UPO':
                        if len(fields)>1:
                            self.run_game.obsticles[fields[2]]=(int(fields[0]),int(fields[1]))
                        else:
                            #print(fields[0])
                            continue
                    elif action=='SUP':
                        self.err_box.set_text(fields[0])

                    elif action=='FRS':
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

                    elif action=='MRS':
                        self.err_box.set_text(fields[0])
                        #self.draw_all()
                    elif action=='GRS':
                        self.rooms_obj.make_lst(pickle.loads(fields[0].encode()))
                        self.err_box.set_text('get refresh')
                        #self.draw_all()
                    elif action == 'JRI':
                        if fields[0]=='Successful':
                            self.err_box.set_text(fields[0])
                            self.rooms_obj.joined=True
                            send_with_size(self.sock,('GOP~').encode())
                    elif action=='ERR':
                        self.err_box.set_text(fields[0])
                    elif action=='BYE':
                        self.can_close=True
            except socket.timeout:
                continue
            except Exception as e:
                print("Listener encountered error:", e)
                self.err_box.set_text(e)
                #self.draw_all()
                break


if __name__=='__main__':
    a=Game()