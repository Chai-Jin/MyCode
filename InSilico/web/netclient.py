#
# client of edgeserver
#

import sys
import json
import socket

PORT = 6369

if __name__=="__main__":
    if (len(sys.argv) != 2):
        print "usage: edgeclient.py [workfolder]"
        exit(0)

    workfolder = sys.argv[1]
    j = {
        'work': 'DEGsearch',
        'workfolder': workfolder
        }

    ret = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", PORT))
        sock.sendall(json.dumps(j) + "\n")
        recv = sock.recv(1024)
        rj = json.loads(recv)
        print rj
        ret = rj['code']
    finally:
        sock.close()

    exit(ret)
