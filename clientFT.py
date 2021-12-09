#! /usr/bin/env python3
from socket import *
import sys, os, time
import select

serverAddr = ('localhost', 50000)
connection = socket(AF_INET, SOCK_DGRAM)
connection.setblocking(False)
filename = ""
previousPacket = ""
final_time = 0
inital_time = 0
rtt = 0


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

timeout = rtt
print("Enter Filename to send")
while True:
    readers, writers, _ = select.select([connection,sys.stdin],[],[])
    if not readers and not writers and not _:
        print("Timeout attempt to send again")
        connection.sendto(previousPacket, serverAddr)

    for reader in readers:
        if reader is connection:
            ##WHAT DO DO ONCE MESSAGE HAS BEEN RECIVED.
            firstmsg, clientAddr = connection.recvfrom(2048)
            segnum, isfilename, paysize, message = openPacket(firstmsg)  # SPLIT METADATA FROM PAYLOAD

            final_time = time.time()
            rtt = final_time - initial_time ##Update RTT
            print("Rount Trip Time: ",rtt)

            #OPEN FILE AND START READING AND SENDING.
            totalseg = getfileSize(filename)
            file = open(filename,"rb")

            if message == "ready": ##Acknolegement of previous seg recived
                for currentRead in read_in_chunks(file,100):
                    if segnum != totalseg+1:
                        packet = encapMessage(currentRead.decode(), segnum , "P")
                        previousPacket = packet ##save a copy incase we need to resend.
                        connection.sendto(packet,serverAddr)
                        segnum += 1
                        print("Sending Segment: " +str(segnum))

                else: ## ONCE FILE HAS BEEN READ.
                    print("DONE sending file.")
                    done_msg = encapMessage(str(totalseg+1),0, "C")
                    connection.sendto(done_msg, serverAddr)
                    file.close()
                    exit(0)
            elif message == "resend":
                print("Attempting to resend packet")
                connection.sendto(previousPacket,serverAddr)

            else:
                print("Sorry server got scared.")

        else:
            filename = sys.stdin.readline()[:-1]
            print("Sending "+str(getfileSize(filename))+" Segments")
            ##ASKING FOR FILENAME AND CHECK IF EXISTS
            if fileExist(filename) == True: #will change back to True later
                msg = encapMessage(filename,0,"F")
                connection.sendto(msg,serverAddr)
                previousPacket = msg ## Save incase we need to resend
                initial_time = time.time()
            else:
                print("Enter 'Real' File ")





