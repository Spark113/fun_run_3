import os
import traceback
import socket
import threading
import pickle
import hashlib
import secrets
import base64
from dataclasses import fields

from encrption.TCP_AES import Decrypt_AES
from encrption.tcp_by_size import send_with_size, recv_by_size
from encrption.AsyncMessages import AsyncMessages
from encrption.RSA import RSA_CLASS
from run_game import run_class

rooms=[]
users = {}
connected = []
AMessages = AsyncMessages()
all_to_die = False
users_rooms={}
def logtcp(direction, tid, byte_data):
    if direction == 'sent':
        print(f'{tid} S LOG: Sent     >>> {byte_data}')
    else:
        print(f'{tid} S LOG: Received <<< {byte_data}')

def load_users():
    global users
    try:
        with open('user.pkl', 'rb') as f:
            users = pickle.load(f)
    except Exception as e:
        print(f'Error loading users.pkl: {e}')
        users = {}

def save_users():
    try:
        with open('user.pkl', 'wb') as f:
            pickle.dump(users, f)
    except Exception as e:
        print(f'Error saving users.pkl: {e}')

def hash_password(password, salt):
    if salt == None:
        salt = secrets.token_hex(16)
    combined = password + salt
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    return hashed, salt

def sign_up(username, password):
    load_users()
    if username in users:
        return 'SUP~Username already exists', False
    hashed_pass, salt = hash_password(password, None)
    users[username] = (hashed_pass, salt)
    save_users()
    return 'SUP~Success', True

def login(username, password, sock):
    try:
        global AMessages
        global connected
        load_users()
        if username not in users:
            return "LOG~User not found", False
        if username in connected:
            return "LOG~User alrady in", False
        user_data = users[username]
        stored_hashed_pass = user_data[0]
        salt = user_data[1]
        hashed_input_pass, salt1 = hash_password(password, salt)
        if hashed_input_pass == stored_hashed_pass:
            AMessages.sock_by_user[username] = sock
            connected.append(username)
            return "LOG~Login Successful", True
        return "LOG~Login Unsuccessful", False
    except Exception as err:
        print(err)

def rsa_key(public_key,rsa_obj):
    key = os.urandom(16)
    print(key)
    other_key = public_key
    rsa_obj.set_other_public(other_key)
    key_enc = rsa_obj.encrypt_RSA(key)
    return key_enc,key

def exit(user_name1):
    global connected
    global users_rooms
    try:
        print(user_name1, connected)
        if user_name1 in connected:
            print('a')
            connected.remove(user_name1)
            print(user_name1,users_rooms.keys())
            if user_name1 in users_rooms.keys():
                print(users_rooms[user_name1].del_player(user_name1))
                del users_rooms[user_name1]
            print(user_name1 in users_rooms.keys(), 'users_rooms')
        return 'BYE~'
    except Exception as err:
        print('err',err)
        return err

def protocol_build_reply(request, sock, user_name1, finish, key,rsa_obj):
    try:
        global connected
        global rooms
        global users_rooms

        reply = ''
        request=request.decode()
        request_code = request[:3]
        request = request.split('~')
        if request_code == 'LGN':
            iv = base64.b64decode(request[3])
            user_name = Decrypt_AES(key, iv, base64.b64decode(request[1])).decode()
            password1 = Decrypt_AES(key, iv, base64.b64decode(request[2])).decode()
            reply, logged = login(user_name, password1, sock)
            print(user_name1, connected)
            return reply, logged, user_name, key

        elif request_code == 'SGU':
            reply, suc = sign_up(request[1], str(request[2]))
            return reply, None, user_name1, key

        elif request_code == 'BYE':
            reply=exit(user_name1)
            finish = True
            return reply,None,user_name1, key

        elif request_code == 'GSR':
            public_key_b64 = request[1]
            print(public_key_b64)
            public_key = base64.b64decode(public_key_b64.encode())
            msg, key = rsa_key(public_key, rsa_obj)
            msg_64=base64.b64encode(msg).decode()
            reply = f'FRS~{msg_64}'
            return reply, None, user_name1, key

        if user_name1 in connected:#if he is logged in only then he can do something if not he have to login in
            if request_code == 'MRS':#make rooms
                rooms.append(run_class(AMessages,request[1]))#request[1]=id
                return 'MRS~Successful',None, user_name1, key

            elif request_code == 'GRS':#get rooms
                rooms_info = {}
                for room in rooms:
                    rooms_info.update(room.to_dic())
                print(rooms_info)
                reply=pickle.dumps(rooms_info)
                return b'GRS~'+reply,None, user_name1, key
            elif request_code == 'JRI':
                for room in rooms:
                    if room.room_id==request[1]:
                        print('got here')
                        room.update_player(user_name1,0,0)
                        users_rooms[user_name1]=room
                return 'JRI~Successful', None, user_name1, key
            elif request_code == 'UPD':#update player
                users_rooms[user_name1].update_pos_exept_me(user_name1,int(request[1]),int(request[2]))
                return 'UPD~Successful', None, user_name1, key
            elif request_code=='UPL':
                users_rooms[user_name1].leaderbord(user_name1,float(request[1]))
                return 'ULL~Successful', None, user_name1, key
            elif request_code == 'GOP':#get others players
                dic_p=users_rooms[user_name1].get_players(user_name1)
                #dic_o=users_rooms[user_name1].get_obstcles(user_name1)
                return b'GOP~'+dic_p, None, user_name1, key
            elif request_code == 'UPO':#update obsticle
                users_rooms[user_name1].update_obsticle(user_name1,int(request[1]),int(request[2]))
                return 'UPO~Successful', None, user_name1, key
        else:
            print(connected,user_name1)
            return 'LOG~you have to login first',None, user_name1, key

        return reply,None,user_name1, key
    except Exception as err:
        print(err)
        return 'ERR~' + str(err), None,user_name1,key

def handle_client(sock,tid,addr):
    global all_to_die
    global AMessages
    global connected
    logged = False#if he logged in if not he cant do anything
    user_name1 = ''
    key = None
    rsa_obj = RSA_CLASS()
    AMessages.add_new_socket(sock)
    finish = False
    print(f'New Client number {tid} from {addr}')
    print('hi')
    to_send=''
    sock.settimeout(0.1)
    while not finish:
        try:
            byte_data = recv_by_size(sock)
            if byte_data == b'':
                print('Seems client disconnected')
                exit(user_name1)
                break

            try:
                to_send, logged, user_name1, key = protocol_build_reply(byte_data, sock, user_name1, finish, key,rsa_obj)
            except Exception as err:
                print(to_send)
                print(err)
                to_send = ''
                finish = False

            if to_send != '':
                if type(to_send)==bytes:
                    send_with_size(sock, to_send)
                else:
                    send_with_size(sock, str(to_send).encode())
            if to_send=='BYE~':
                #exit(user_name1)
                finish=True
                print(finish,'finish')
                print('bye')


        except socket.timeout:
            pending = AMessages.get_async_messages_to_send(sock)
            for m in pending:
                send_with_size(sock, m)
            continue
        except ConnectionResetError as err:
            exit(user_name1)
            print('bye bye',err)
            finish=True
        except Exception as err:
            print(f'General Error: {err} - exiting client loop')
            print(traceback.format_exc())
            break

def main():
    global all_to_die
    global AMessages

    AMessages = AsyncMessages()

    threads = []
    srv_sock = socket.socket()
    srv_sock.bind(('0.0.0.0', 3001))
    srv_sock.listen(20)

    async_messages = AsyncMessages()

    i = 0
    while True:
        cli_sock, addr = srv_sock.accept()
        async_messages.add_new_socket(cli_sock)
        t = threading.Thread(target=handle_client, args=(cli_sock, str(i), addr))
        t.start()
        i += 1
        threads.append(t)
        if all_to_die:
            for t in threads:
                t.join()
            break

    srv_sock.close()
    print('Bye ..')

if __name__ == '__main__':
    main()



