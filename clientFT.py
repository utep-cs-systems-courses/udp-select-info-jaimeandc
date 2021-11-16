#! /usr/bin/env python3
from socket import *
import sys, os
import select

serverAddr = ('localhost', 50000)
connection = socket(AF_INET, SOCK_DGRAM)
connection.setblocking(False)
filename = ""


def read_in_chunks(file,size):
    while True:
        chunk = file.read(size)
        if chunk:
            yield chunk
        else:
            break
def fileExist(filename):
    file_exists = os.path.exists(filename)
    if file_exists == True:
        return True
    else:
        return False
def getfileSize(file):
    file_size = os.path.getsize(file)
    file_size = file_size // 100
    return file_size

def readfile(file):
    file=open(file,"rb")


def encapMessage(payload, segnum, msgPart): # Will add send/recv & isfilename?
    segnum = segnum.to_bytes(2, sys.byteorder)#Save segment num to byte array
    segnum = bytearray(segnum)
    msgPart = bytearray(msgPart.encode())#Save if message is filename message.
    paysize = len(payload) # get length of payload and save to bytearray
    paysizebyte = paysize.to_bytes(2,sys.byteorder)
    paysizebyte = bytearray(paysizebyte)
    payload = bytearray(payload.encode()) #save payload in bytearray
    packet = segnum + msgPart + paysizebyte + payload #Concat "packet".
    return packet
def openPacket(packet):
    packet = bytearray(packet)
    segnum = packet[:2] #First 2 bytes are segnum
    segnum = int.from_bytes(segnum,sys.byteorder)
    msgPart = packet[2:3]  #Next byte is msgPart
    paysize = packet[3:5]  #Last 2 bytes is length of payload.
    paysize = int.from_bytes(paysize,sys.byteorder)
    payload = packet[-paysize:]
    return segnum, msgPart.decode(), paysize, payload.decode()


while True:
    readers, writers, _ = select.select([connection,sys.stdin],[],[])

    for reader in readers:
        if reader is connection:
            ##WHAT DO DO ONCE MESSAGE HAS BEEN RECIVED.
            firstmsg, clientAddr = connection.recvfrom(2048)
            segnum, isfilename, paysize, message = openPacket(firstmsg) # SPLIT METADATA FROM PAYLOAD
            print("MSG_FROM_SERVER:",message)
            totalseg = getfileSize(filename)
            #OPEN FILE AND START READING AND SENDING.
            file = open(filename,"rb")
            if message == "ready":
                for currentRead in read_in_chunks(file,100):
                    if segnum != totalseg+1:
                        #currentRead = file.read(100)
                        print(currentRead)
                        print("currentseg:"+ str(segnum) + " totalseg:" + str(totalseg))
                        packet = encapMessage(currentRead.decode(), segnum , "P")
                        connection.sendto(packet,serverAddr)
                        segnum += 1
                else:
                    print("DONE sending file.")
                    sendCheck = encapMessage(str(totalseg+1).encode(),0, "C")
                    file.close()
                    exit(0)

            else:
                print("IDK WHAT YOUR ASKING FROM ME... YET")





                    #packet = encapMessage(currentRead.decode(), currentseg, "N")
                    #connection.sendto(packet,serverAddr)
                #for currentRead in read_in_chunks(file,100):
                #    print(currentRead.decode())
                #    packet = encapMessage(currentRead.decode(), segnum, "N")
                #    connection.sendto(packet,serverAddr)
                #    segnum + 1

        else:
            filename = sys.stdin.readline()[:-1]
            print(getfileSize(filename))
            if fileExist(filename) == True: #will change back to True later
                msg = encapMessage(filename,0,"F")
                connection.sendto(msg,serverAddr)


            else:
                print("Enter 'Real' File ")





