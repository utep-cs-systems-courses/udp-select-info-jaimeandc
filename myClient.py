#! /usr/bin/env python3

from socket import *
import os.path
import sys, re
SEPSYMBOL = '|-&-|'
# default params
serverAddr = ('localhost', 50001)

def read_in_chunks(file,size):
    while True:
        chunk = file.read(size)
        if chunk:
            yield chunk
        else:
            return



def usage():
    print("usage: %s [--serverAddr host:port]"  % sys.argv[0])
    sys.exit(1)

try:
    args = sys.argv[1:]
    while args:
        sw = args[0]; del args[0]
        if sw == "--serverAddr":
            addr, port = re.split(":", args[0]); del args[0]
            serverAddr = (addr, int(port))
        else:
            print("unexpected parameter %s" % args[0])
            usage();
except:
    usage()


payload = bytearray()
clientSocket = socket(AF_INET, SOCK_DGRAM)
filename = input("Input name of file:")
file_exists = os.path.exists(filename) # check if file exist in order to send
if file_exists == True:
    try:
        segCount = 0
        with open(filename, "rb") as f:
            for chunk in read_in_chunks(f, 100): #Read file and split into 100byte chunks.
                segCount = segCount + 1
## SEND THE FILENAME AND SEG COUNT FIRST BEFORE WE EVEN BOTHER SENDING MSG.
        clientSocket.sendto(filename.encode(), serverAddr)  ## Send file name and segment count first.
        clientSocket.sendto(str(segCount).encode(), serverAddr) ## Send number of segments in file.
        InitACK, serverAddrPort = clientSocket.recvfrom(2048)
        if InitACK.decode() == "OK": ##CHECK IF "OK" IF "NOT-OK" "PANIC"
            print("Sending : '%s'" % filename)
            with open(filename, "rb") as f:
                sendcount = 0
                for chunk in read_in_chunks(f, 100):  # Read file and split into 100byte chunks.
                    if sendcount != segCount+1:
                        chunk = bytearray(chunk)
                        chunklen = len(chunk)

                        ##CHANGE TO SAVE INTO BYTEARRAY AND CONCAT
                        #headinfo = SEPSYMBOL + str(chunklen) + SEPSYMBOL + str(sendcount)
                        #header = bytearray(headinfo)

## CURRENT LAYOUT OF MESSAGE <><sep><chunklen><sep><sendcount> STILL NEED TO ADD START/END & SEND/RECV
                        chunk.extend(str(SEPSYMBOL).encode())
                        chunk.extend(str(chunklen).encode())
                        chunk.extend(str(SEPSYMBOL).encode())
                        chunk.extend(str(sendcount).encode())
                        print("Sending seg number : ", sendcount)
                        clientSocket.sendto(chunk,serverAddr) ## Send Chunk and wait for ACK
                        recvACK, serverAddrPort = clientSocket.recvfrom(2048)
                        print("Server got seg: ", int(recvACK.decode()))
                        if int(recvACK.decode()) != sendcount: ## Check if we need to resend.
                            clientSocket.sendto(chunk, serverAddr)
                        else:
                            sendcount = sendcount + 1

                    else:
                        break
        else:
            print("Sorry something went wrong now you can PANIC!!!")

    finally:
        print("Done")
        clientSocket.close()

else:
    print("'%s' does not exists." % filename)
