"""COSC 264 Socket Programming Assignment server.py
Charlotte Collie - cco128 78984625"""

from socket import *
import sys

MAGIC_NUM  = 0xAE73

message_dict = {} #dictionary to store messages

def main():
    sock = None
    conn = None

    if len(sys.argv) != 2: #right num of arguments given
        print("Wrong number of arguments")
        exit()
        
    port = int(sys.argv[1])

    if port < 1024 or 64000 < port: #if right port size
        print("Port value not within acceptable range")
        exit()

    sock = socket(AF_INET, SOCK_STREAM)
    
    try: #trys to bind the port
        sock.bind(("0.0.0.0", port))
    except:
        print("Binding failed")

    try: #listens
        sock.listen()
    except:
        print("Listening failed")


    while True: #cool loop!!!!!!
        conn, addr = sock.accept()
        print(f"Connceted to IP = {addr[0]}  Port = {port}")
        data = conn.recv(10000)
    
        magic_num  = data[:2]
        magic_num = int.from_bytes(magic_num, byteorder='big')
        
        if magic_num != MAGIC_NUM: #magic num checked here so its only checked once, makes sure it is a valid request
            print('Magic number error')
            exit()

        id = data[2]
        
        if id == 2:
            create(data)
            conn.close()
        
        elif id == 1:
            read(data,conn)
            conn.close()

        else:
            print("Error")
            exit()



def read(data, conn): #i think this is sending it right, just need client side
    """sends recived messages to the client"""
    #rec_len = 0, message len = 0
    name_len = data[3]

    if name_len < 1: #checks right name length
        print("Name not valid")
        exit()

    name = data[7 : 7 + name_len]
    name = name.decode("UTF-8") #gettiing name

    if name not in message_dict:
        print("That name isnt in the database")
        exit()

    num_items = len(message_dict[name])

    if num_items > 255:
        num1 = MAGIC_NUM >> 8
        num2 = MAGIC_NUM & 0x00FF
        message_response = bytearray([num1, num2, 3, 254, 1])
        #print('meow')

    elif num_items == 0:
        num1 = MAGIC_NUM >> 8
        num2 = MAGIC_NUM & 0x00FF
        message_response = bytearray([num1, num2, 3, 0, 0, 0, 0])
        sent = conn.send(message_response)

    else:
        num1 = MAGIC_NUM >> 8
        num2 = MAGIC_NUM & 0x00FF
        message_response = bytearray([num1, num2, 3, num_items, 0])

    min_val = min(num_items, 255)
    rep_list = []

    for i in range(min_val): #for loop to send data back to client , dont want it to exceed 255
        message_response_2 = 0
        pack = message_dict[name][0]
        message_dict[name].pop(0)

        sender = pack[0]
        mess = pack[1]
        sender_len = len(sender)
        mess_len = len(mess)
        mess = bytearray(mess, 'UTF-8')
        sender = bytearray(sender, 'UTF-8')
        message_response_2 = message_response + bytearray([sender_len, mess_len])
        message_response_2 = message_response_2 +  sender + mess
        rep_list.append(message_response_2) #list to put the bytearrays in
    
    i = 0
    #print(rep_list)
    while i != (min_val): #goes through the list and sends one at a time
        #print(rep_list[i])
        conn.send(rep_list[i])
        i += 1 

    #i did this cause it kept sending them together and this was the best way i could get them seperate



def create(data):#this works
    """stores sent messages in a dictionary"""
    #uncpacking all vars needed from data
    reciver_len = data[4]
    name_len = data[3]
    message_data = data[7 + name_len + reciver_len :]
    message_len = len(message_data)
    message_data = message_data.decode('UTF-8')
    reciver = data[7 + name_len: 7 + name_len + reciver_len] #tbh idk what ive done i thought this should be a 7, nvm fixed it
    reciver = reciver.decode('UTF-8')
    name = data[7:7 + name_len]
    name = name.decode("UTF-8")
    
    if name_len < 1: #checks right name length
        print("Name not valid")
        exit()
    
    if reciver_len < 1: #checks right reciver length
        print("Reciver not valid")
        exit()

    if message_len < 1: #checks right message length
        print("Message not valid")
        exit()


    if reciver not in message_dict: #if not in the dict
        message_dict[reciver] = [(name, message_data)]
    
    else: #if in the dict
        message_dict[reciver].append((name, message_data))
    print(f"Message from {name} stored for {reciver}")


main()