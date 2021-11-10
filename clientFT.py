#! /usr/bin/env python3
from socket import *
import sys
import select
serverAddr = ('localhost', 50000)
connection = socket(AF_INET, SOCK_DGRAM)

while True:
    readers, _, _ = select.select([connection,sys.stdin],[],[])
    for reader in readers:
        if reader is connection:
            firstmsg, clientAddr = connection.recvfrom(1000)
            print(firstmsg.decode())

        else:
            print("Input lowercase msg")
            msg = sys.stdin.readline()[:-1]
            connection.sendto(msg.encode(),serverAddr)
