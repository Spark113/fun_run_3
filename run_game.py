from time import sleep

import pygame
import threading
import pickle
import math
import sys

class run_class():#
    def __init__(self,AMessages,id):
        self.AMessages=AMessages
        self.room_id=id
        self.players={}
        self.obstcles={}
        #self.t=threading.Thread(target=self.run_obsticle)
        #self.t.start()
        self.stop=False
        self.playing=False
        self.leaderbord_dict={}
    def update_player(self,name,x,y):
        self.players[name]=((x,y))
        self.playing=True
        if name not in self.players.keys():
            for k, v in self.players.items():
                if k != name:
                    self.AMessages.put_msg_by_user(b'GOP~'+self.get_players(k),k)
                    #self.AMessages.put_msg_by_user(b'GOO~' + self.get_obstcles(k), k)#get other obsticals


    def del_player(self,name):
        del self.players[name]
        if len(self.players) <= 0:
            self.playing = False
        if name in self.players.keys():
            for k, v in self.players.items():
                if k != name:
                    self.AMessages.put_msg_by_user(b'GOP~'+self.get_players(k),k)
                    #self.AMessages.put_msg_by_user(b'GOO~' + self.get_obstcles(k), k)  # get other obsticals
            print('done')
            return 'deleted it'

    def get_players(self,name):
        p={}
        for k,v in self.players.items():
            if k!=name:
                p[k]=v
        return pickle.dumps(p)

    def get_obstcles(self,name):
        p = {}
        for k, v in self.players.items():
            if k != name:
                p[k] = v
        return pickle.dumps(p)

    def to_dic(self):
        return {self.room_id:len(self.players)}


    def update_pos_exept_me(self,name,x,y):
        self.players[name]=(x,y)
        for k,v in self.players.items():
            if k != name:
                self.AMessages.put_msg_by_user(f'UPP~{x}~{y}~{name}', k)  # UPP = update pos player

    def update_obsticle(self,name,x,y):
        for k, v in self.players.items():
            if k != name:
                self.AMessages.put_msg_by_user(f'UPO~{x}~{y}~{name}', k)  # UPP = update pos player
    def leaderbord(self,name,time):
        self.leaderbord_dict[name]=time
        self.leaderbord_dict=self.sort_dict(self.leaderbord_dict)
        print(len(self.leaderbord_dict.keys()),len(self.players.keys()))
        print(self.leaderbord_dict,self.players)
        if len(self.leaderbord_dict.keys())==len(self.players.keys()):
            print('ended here',self.leaderbord_dict)
            p_dict=pickle.dumps(self.leaderbord_dict)
            for k, v in self.players.items():
                print('sent to: ',k)
                self.AMessages.put_msg_by_user(b'UPL~'+p_dict, k)  # UPP = update players leaderbord
    def sort_dict(self,d:dict):
        sorted_dict={}
        while len(d.keys())>0:
            min_key=self.find_min(d)
            sorted_dict[min_key]=d[min_key]
            del d[min_key]
        return sorted_dict
    def find_min(self,d):
        min_key=None
        min_val=sys.maxsize
        for k, v in d.items():
            if v<min_val:
                min_key=k
                min_val=v
        return min_key