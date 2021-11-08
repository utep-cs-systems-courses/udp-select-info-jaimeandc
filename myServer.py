#! /usr/bin/env python3

import sys
import tkinter.filedialog
from socket import *
from select import select
import time

upperServerAddr = ("", 50000)   # any addr, port 50,000
getFileNamesAddr = ("", 50001)
receiveFileAddr = ("", 50002)

filename = ""
seporator = "|-&-|"
filepayload=[]

    

def uppercase(sock):# check this socket 'sock' if we have somthing to rec.
  "run this function when sock has rec'd a message"
  message, clientAddrPort = sock.recvfrom(2048)
  print("from %s: rec'd '%s'" % (repr(clientAddrPort), message))
  modifiedMessage = message.decode().upper().encode()
  sock.sendto(modifiedMessage, clientAddrPort)

def getFile(sock):
  filename, clientAddrPort = sock.recvfrom(2048) ## Get filename from client
  print("from %s: rec'd file: '%s'" % (repr(clientAddrPort), filename.decode())) ## send ACK
  segCount, clientAddrPort = sock.recvfrom(2048) ## Get number of segments that will be sent
  segCount = int(segCount.decode())
  print("from %s: segCount: '%d'" % (repr(clientAddrPort), segCount))
  filenameACK = "OK"
  sock.sendto(filenameACK.encode(), clientAddrPort) ## Send ACK that file is ready to be sent

  firstpayload, clientAddrPort = sock.recvfrom(2048) ##Get first part of payload
  payloadlist = firstpayload.decode()
  #print(payloadlist)
  payload, chunklen, recvCount = payloadlist.split(seporator) ##Split encap message
  sock.sendto(recvCount.encode(), clientAddrPort)
  filepayload.append(payload) ##Append first part of payload to array
  recvCount = int(recvCount)
  print(recvCount)

  while recvCount != segCount :
    payload_seg, clientAddrPort = sock.recvfrom(2048)
    payloadcont = payload_seg.decode()
    payload, chunklen, recvCount = payloadcont.split(seporator)
    filepayload.append(payload)
    recvCount = int(recvCount)
    print("Got seg # ",recvCount)
    sock.sendto(str(recvCount).encode(), clientAddrPort)
    recvCount = recvCount + 1
    #try:
    #  payload_seg, clientAddrPort = sock.recvfrom(2048)
    #  payloadcont = payload_seg.decode()
    #  payload, chunklen, recvCount = payloadcont.split(seporator)
    #  filepayload.append(payload)
    #  recvCount = int(recvCount)
    #  print("Got seg # ", recvCount)
    #  recvCount = recvCount + 1
    #except:
    #  pass

  print("------------------FILE_PAYLOAD-----------------------")
  print(filepayload)


    #segCountACK = segCount
    #sock.sendto(segCountACK, clientAddrPort)

  
#Create the socket.
upperServerSocket = socket(AF_INET, SOCK_DGRAM)
upperServerSocket.bind(upperServerAddr) # bind to uppserServerAddr port
upperServerSocket.setblocking(False) #tell the socket to never block so when you try to do somthing it ownt block.

FileNameServerSocket = socket(AF_INET, SOCK_DGRAM)
FileNameServerSocket.bind(getFileNamesAddr)
FileNameServerSocket.setblocking(True)



# map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}              # broken

timeout = 15                     # select delay before giving up, in seconds

# function to call when upperServerSocket is ready for reading
readSockFunc[upperServerSocket] = uppercase
#readSockFunc[lowerServerSocket] = lowercase
readSockFunc[FileNameServerSocket] = getFile
writeSockFunc[FileNameServerSocket] = getFile


print("ready to receive")
while 1:
  readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                list(writeSockFunc.keys()), 
                                                list(errorSockFunc.keys()),
                                                timeout)
  if not readRdySet and not writeRdySet and not errorRdySet:
    print("timeout: no events")
  for sock in readRdySet:
    readSockFunc[sock](sock)
  for sock in writeRdySet:
    writeSockFunc[sock](sock)
