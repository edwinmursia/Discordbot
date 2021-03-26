#FOR TESTING PURPOSES ONLY

from random import randint
import time


import zmq
import time
import threading


class publisher:

    # Address a port for ZMQ socket
    SOCKET_PORT = "tcp://localhost:1234"

    # Attempt a connection to ZMQ socket
    ctx = zmq.Context()

    sock = ctx.socket(zmq.PUB)
    sock.connect(SOCKET_PORT)

    def __init__(self, id):

        self.SERVER_ID = id
        print("Starting status message loop...")
        self.sendServerStatusMessage()

    # Server status message sending function
    def sendServerStatusMessage(self):
        currentTime = int(time.time())
        msg = "%d, %d" %(self.SERVER_ID, currentTime)
        self.sock.send_string(msg)
        # Loop sendServerStatusMessage every 3 seconds
        threading.Timer(3, self.sendServerStatusMessage).start()



servers = 0
while servers < 5:
    publisher(servers)
    servers += 1