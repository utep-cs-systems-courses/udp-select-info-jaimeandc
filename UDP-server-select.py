import sys
from socket import *
from select import select

upperServerAddr = ("", 50000)  # any addr, port 50,000

def encapMessage(payload, segnum, msgPart): # Will add send/rec
    segnum = segnum.to_bytes(2, sys.byteorder)#Save segment num
    segnum = bytearray(segnum)
    msgPart = bytearray(msgPart.encode())#Save if message is fi
    paysize = len(payload) # get length of payload and save to
    paysizebyte = paysize.to_bytes(2,sys.byteorder)
    paysizebyte = bytearray(paysizebyte)
    payload = bytearray(payload.encode()) #save payload in byte
    packet = segnum + msgPart + paysizebyte + payload #Concat "
    return packet
def openPacket(packet):
    packet = bytearray(packet)
    segnum = packet[:2]
    segnum = int.from_bytes(segnum,sys.byteorder)
    msgPart = packet[2:3]
    paysize = packet[3:5]
    paysize = int.from_bytes(paysize,sys.byteorder)
    payload = packet[-paysize:]
    return segnum, msgPart.decode(), paysize, payload.decode()
def getFile(sock):
    "run this function when sock has rec'd a message"
    message, clientAddrPort = sock.recvfrom(2048)
    #print("from %s: rec'd '%s'" % (repr(clientAddrPort), message))
    segnum, msgPart, paysize, message = openPacket(message)
    currentfile = ""
    if msgPart == "F": #If filename is sent
        print("Received filename :", message)
        currentfile = message
        message = encapMessage("ready",segnum, "P")
        sock.sendto(message, clientAddrPort)
    elif msgPart == "P": #If file payload is sent
        print("Receiving segment: ",segnum," - ", message)
        #file = open(currentfile,"a")
        message = encapMessage('ready',segnum,"P")
        #file.close()
        sock.sendto(message, clientAddrPort)
    elif msgPart == "C":

        print("Done sending file.")




upperServerSocket = socket(AF_INET, SOCK_DGRAM)
upperServerSocket.bind(upperServerAddr)
upperServerSocket.setblocking(False)

# map socket to function to call when socket is....
readSockFunc = {}  # ready for reading
writeSockFunc = {}  # ready for writing
errorSockFunc = {}  # broken

timeout = 5  # select delay before giving up, in seconds

# function to call when upperServerSocket is ready for reading
readSockFunc[upperServerSocket] = getFile

print("ready to receive")
while 1:
    readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                  list(writeSockFunc.keys()),
                                                  list(errorSockFunc.keys()),
                                                  timeout)
    if not readRdySet and not writeRdySet and not errorRdySet:
        print("timeout: no events.") ## NEED TO ADD TIMOUT FEATURE.
    for sock in readRdySet:
        readSockFunc[sock](sock)