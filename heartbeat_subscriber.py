import zmq
import time
import threading

class hb_subscriber:    

    #Address of the port to listen to
    SOCKET_ADDRESS = "tcp://*:1234"
    #Time in seconds to wait to run receiveMessages() again
    TIMER_TIMEOUT = 1

    #Set up socket
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.bind(SOCKET_ADDRESS)
    sock.subscribe("") # Subscribe to all topics

    #initialize with a reference to an instance of serverStatusStorage
    def __init__(self, storage):
        self.serverStorage = storage

        #Start receiving messages
        print("Starting receiver loop")
        self.receiveMessages()

    def receiveMessages (self):
        try:
            print("In receiveMessages")

            message = self.sock.recv_string(flags = zmq.NOBLOCK)
            #Save received timestamp
            self.serverStorage.setTimestamp(message)

            #print received message and servers list for debugging purposes
            print("Received: " + message)
            servers = self.serverStorage.getServersList()
            for x in servers:
                print(x)

        except zmq.ZMQError as e:

            #Error no.88 raised when socket is closed, opening a new one
            if e.args[0] == 88:
                print("Error in subscriber: Socket closed, creating new one and reconnecting")
                newSock = self.ctx.socket(zmq.SUB)
                newSock.bind(self.SOCKET_ADDRESS)
                newSock.subscribe("")

                self.sock = newSock

            #Error no.11 raised when no new messages were received, no actions needed
            elif e.args[0] == 11:
                pass

            else:
                print(f"Error in subscriber: ZMQError {e.args}: {e}. Don't know how to handle this")

        
        
        #Loop this function every 5 seconds or how many seconds TIMER_TIMEOUT is
        threading.Timer(self.TIMER_TIMEOUT, self.receiveMessages).start()