# botModules.py contains modules which are used by botHandler
# authors: 1, 2 and Edwin Mursia

import time
import heartbeat_subscriber, serverStatusStorage

# initializing zeroMQ side
storage = serverStatusStorage.dataSaver()
heartbeat_subscriber.hb_subscriber(storage)

# fill here if more commands are added
allCommands = (
        '```!status "serverID" = Shows status of a specific server```'
        '```!help = Shows all of the commands```'
        '```!allstatuses = Shows status of all the servers```'
        '```!allservers = Shows names and ID\'s of all the servers```'
        '```!downtime "serverID" "startdate(DD.MM.YYYY-HH:MM:SS)" "enddate(DD.MM.YYYY-HH:MM:SS)" = Shows downtimes on a given timescale```'
        '```!addserver "name" "serverID" = Adds a new server to database```'
        '```!deleteserver "serverID"= Deletes a server from database```'
    )

# FUNCTIONS FOR DISCRODBOT.PY TO USE

# returns all commands that are available to the user
def showCommands():
    return allCommands

# returns server's current status
def getCurrentStatus(serverID):
    # get list of current server statuses
    allCurrentStatuses = storage.getServersList()
    
    # pick correct server status based on serverID
    for status in allCurrentStatuses:
        if status["serverID"] == serverID:
            currentTimestamp = status["last_heard"]
            currentTimestamp = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(currentTimestamp))
            serverID = str(serverID)
            currentStatus = str(status["online"])
            answer = f"```Status for server {serverID}: at {currentTimestamp} online {currentStatus}```"
            return answer  

# returns current status for all servers
def getAllCurrentStatuses():  
    # get list of current server statuses
    allCurrentStatuses = storage.getServersList()
    allAnswers = []

    for status in allCurrentStatuses:
        answerDict = {}
        answerDict["serverID"] = str(status["serverID"])
        # convert epoch timestamps to proper format
        answerDict["timestamp"] = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(status["last_heard"]))
        answerDict["online"] = status["online"]
        allAnswers.append(answerDict)

    return allAnswers

#used to obtain date from a user
def convertToEpoch(timestamp):
    userIn = timestamp
    pattern = '%d.%m.%Y-%H:%M:%S'
    epoch = int(time.mktime(time.strptime(userIn, pattern)))
    return epoch

def addServer(serverID):
    storage.addServer(serverID)

def deleteServer(serverID):
    storage.deleteServer(serverID)
