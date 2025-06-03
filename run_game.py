from time import sleep

import pygame
import threading




class run_class():#
    def __init__(self,id):
        self.room_id=id
        self.players={}
        self.obstcles={}
        self.t=threading.Thread(target=self.run_obsticle)
        #self.t.start()
        self.stop=False
    def update_player(self,name,x,y):
        self.players[name]=((x,y))

    def update_obsticle(self,name,x,y):
        self.obstcles[name]=((x,y))#the name will be the img //mabey i sould make it a class that have time to live name and x,y

    def get_all_exept_me(self,name):
        p={}
        for k,v in self.players:
            if k!=name:
                p[k]=v
        return p
    def to_dic(self):
        return {self.room_id:len(self.players)}

    def run_obsticle(self):
        while not self.stop:
            sleep(0.5)
            if len(self.obstcles)>0:
                for k,v in self.obstcles:
                    v[0]=v[0]+2

