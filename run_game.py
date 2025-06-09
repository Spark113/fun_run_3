from time import sleep

import pygame
import threading
import pickle
import math

class run_class():#
    def __init__(self,AMessages,id):
        self.AMessages=AMessages
        self.room_id=id
        self.players={}
        self.obstcles={}
        self.t=threading.Thread(target=self.run_obsticle)
        #self.t.start()
        self.stop=False
        self.playing=False
    def update_player(self,name,x,y):
        if name not in self.players.keys():
            print("works")
            for k, v in self.players.items():
                if k != name:
                    self.AMessages.put_msg_by_user(b'GOP~'+self.get_players(k),k)
        self.players[name]=((x,y))
        self.playing=True

    def update_obsticle(self,name,x,y):
        self.obstcles[name]=((x,y))#the name will be the img //mabey i sould make it a class that have time to live name and x,y

    def del_player(self,name):
        if name in self.players.keys():
            for k, v in self.players.items():
                if k != name:
                    self.AMessages.put_msg_by_user(b'GOP~'+self.get_players(k),k)
            del self.players[name]
            if len(self.players)<=0:
                self.playing = False
            return 'deleted it'

    def get_players(self,name):
        p={}
        for k,v in self.players.items():
            if k!=name:
                p[k]=v
        return pickle.dumps(p)

    def to_dic(self):
        return {self.room_id:len(self.players)}

    def run_obsticle(self):
        while not self.stop:
            sleep(0.5)
            if len(self.obstcles)>0:
                for k,v in self.obstcles:
                    v[0]=v[0]+2

    def update_pos_exept_me(self,name,x,y):
        self.players[name]=(x,y)
        for k,v in self.players.items():
            if k != name:
                self.AMessages.put_msg_by_user(f'UPP~{x}~{y}~{name}', k)  # UPP = update pos player
                print(k)

