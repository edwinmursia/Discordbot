import zmq
import time
import threading

#File path to the configuration file that has the server's ID number
CONFIG_FILE = "config.txt"
SERVER_ID = 0


#Read Server ID from config file
try:
    file = open(CONFIG_FILE)
    line = file.readline()
    file.close()

    SERVER_ID = int(line)

except FileNotFoundError:
    print(f"File <{CONFIG_FILE}> Not Found")
    #Exit from this program
    exit()

# Address a port for ZMQ socket
SOCKET_PORT = "tcp://localhost:1234"

# Define the delay for threading timer
TIMER_TIMEOUT = 30

# Attempt a connection to ZMQ socket
ctx = zmq.Context()
try: 
    print("Establishing a ZMQ socket")
    sock = ctx.socket(zmq.PUB)
    sock.connect(SOCKET_PORT)
    
except zmq.ZMQError as e:
    print("Error connecting to a socket")

# Start sending messages
print("Starting status message loop...")

# Server status message sending function
def sendServerStatusMessage():
    currentTime = int(time.time())
    msg = "%d, %d" %(SERVER_ID, currentTime)
    sock.send_string(msg)
    print("Sent message")
    # Loop sendServerStatusMessage every 30 seconds
    threading.Timer(TIMER_TIMEOUT, sendServerStatusMessage).start() 

sendServerStatusMessage()

#sock.close()
#ctx.term()