"""COSC 264 Socket Programming Assignment client.py
Charlotte Collie - cco128 78984625"""

from socket import * 
import sys

MAGIC_NUM  = 0xAE73


def main():
    sock = None
    message_request = bytearray(0)

    try:
        if len(sys.argv) != 5:
            print("Wrong number of command line arguments")
            exit()

        port = int(sys.argv [2])
        process = sys.argv[4]

        if port < 1024 or 64000 < port:
            print("Port value not within acceptable range")
            exit()

        services = getaddrinfo(sys.argv[1], port, AF_INET, SOCK_STREAM)
        family, type, proto, canonname, address = services[0]
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(address)

        if process == 'create': #checks if its a create
            create(sock)

        elif process == 'read': #check if its read
            read(sock)
         
        else: 
            print("Not a valid request")
            exit()


    except gaierror:
        print("Host does not exist")
    except OSError as err:
        print(f"ERROR: {err}")

    finally:
        if sock != None:
            sock.close()


def read(sock):
    name = sys.argv[3]
    name_len = len(name)
    message_len = 0
    rec_len = 0

    num1 = MAGIC_NUM >> 8
    num2 = MAGIC_NUM & 0x00FF
    message_request = bytearray([num1, num2])
    message_request = message_request + bytearray([1, name_len, rec_len])
    message_len = message_len >> 8
    message_len2 = message_len & 0x00FF
    message_request = message_request + bytearray([message_len, message_len2])
    name = bytearray(name, 'UTF-8')
    message_request = message_request + name #adds encoded strings to message request
    sent = sock.send(message_request) #sends message request to server
    
    received  = sock.recv(4096)

    magic_num = received[:2]
    magic_num = int.from_bytes(magic_num, byteorder='big')

    if magic_num != MAGIC_NUM: #magic num checked here so its only checked once
            print('Magic number error')
            exit()

    amount = received[3]
    more_msg = received[4]
    #print(more_msg)

    if more_msg == 1:
        amount = 255

    name = received[7:7 + name_len]

    if amount == 0:
        print(f"No messages for {sys.argv[3]}")
        exit()
    
    sender_len = received[5]
    sender = received[7 : 7 + sender_len]
    message = received[7 + sender_len:]

    print(f"Sender: {sender.decode('UTF-8')} Message: {message.decode('UTF-8')}")
    
    #received  = sock.recv(10000)
    #print(received)

    for i in range(0, amount-1): #goes through the recvied byte array and prints out messages
        received  = sock.recv(4096)
        print(received)
        sender_len = received[5]
        message = received[7 + sender_len:]
        sender_len = received[5]
        message = received[7 + sender_len:]
        sender = received[7 : 7 + sender_len]
        print(f"Sender: {sender.decode('UTF-8')} Message: {message.decode('UTF-8')}")

    if more_msg == 1:
        print("Max amount of messages printed in server")

    else:
        print("All messages printed")

 

    sock.close()
    exit() #exit after its done its bits


def create(sock):
    name = sys.argv[3]
    name_len = len(name)
    rec = input("Who is the reciever of this message: ") #gets names of reciver
    encoded_rec = rec.encode('UTF-8')

    while len(rec) < 1 or len(encoded_rec) >= 255: #checks that the reciver is valid
        rec = input("Not a valid receiver, please enter another: ")

    message = input("Enter the message: ")
    encoded_message = message.encode('UTF-8')

    while len(message) < 1 or len(encoded_message) >= 255: #checks that the message is valid
        message = input("Not a valid message, please enter another: ")

    rec_len = len(rec)
    message_len = len(message)

    num1 = MAGIC_NUM >> 8
    num2 = MAGIC_NUM & 0x00FF
    message_request = bytearray([num1, num2, 2, name_len, rec_len])
    message_len = message_len >> 8
    message_len2 = message_len & 0x00FF
    message_request = message_request + bytearray([message_len, message_len2])
    name = bytearray(name, 'UTF-8')
    rec = bytearray(rec, 'UTF-8')
    message= bytearray(message, 'UTF-8')
    message_request = message_request + name + rec + message #adds encoded strings to message request
    sent = sock.send(message_request) #sends message request to server


main()