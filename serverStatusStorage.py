import time

import pymongo
import os
from cyberBot import connection

class dataSaver():
    #Get a database client from botfiles.connection.py
    client = connection.dbClient()

    # Servers = [{"serverID", "last_heard", "online"}, {"serverID", "last_heard", "online"}, ...]
    servers = []

    #(id, online), (id, online)
    inDatabase = []

    def __init__(self):
        #Find server ids from id collection in the database, for each add to the servers list
        for id in self.client.idcollection.find():
            self.addServer(id["serverID"])

    def addServer (self, id):
        #Check if there already is a server with the id
        for server in self.servers:
            if server["serverID"] == id:
                return

        #Add a dictionary to the servers list
        self.servers.append({"serverID": id, "last_heard": 0, "online": False})

    #Delete a server from the server's list
    def deleteServer (self, id):
        for server in self.servers:
            if server["serverID"] == id:
                self.servers.remove(server)

    def getServersList(self):
        #Check for server's that are down
        self.markCurrentlyDownServers()
        return self.servers

    #Marks servers last heard from over 120s ago as not online
    def markCurrentlyDownServers (self):

        currentTime = int(time.time())

        for server in self.servers:
            if server["online"]:
                timeStamp = int(server["last_heard"])
                if currentTime - timeStamp > 120:
                    server["online"] = False
                    server["last_heard"] = currentTime

                    #Send to database
                    self.sendToDataBase(server)

    #Data is in string form and contains "serverID, timestamp"
    def setTimestamp (self, data):
        id, timestamp = data.split(",")
        id = int(id)
        timestamp = int(timestamp)

        #Check if the given server id is valid: there is a dictionary with the same serverID in the list
        #Remove that dictionary before adding the new one
        valid = False
        for server in self.servers:
            if server["serverID"] == id:
                valid = True
                self.servers.remove(server)
        
        if not valid:
            return
    
        dataDict = {}
        dataDict["serverID"] = id
        dataDict["last_heard"] = timestamp
        dataDict["online"] = True

        self.servers.append(dataDict)

        #Send this to database
        self.sendToDataBase(dataDict)

    #Sending data to server status database
    #Data is {id, timestamp, online}
    def sendToDataBase (self, data):
        #Check if this data is actually already in the database
        for status in self.inDatabase:

            #If the same data is already in database, no actions needed
            if data["serverID"] == status["serverID"] and data["online"] == status["online"]:
                return
            
            #If server was previosly down
            if data["serverID"] == status["serverID"] and status["online"] == False:
                self.inDatabase.remove(status)
                #to do: do something
                continue

            #If this server is marked with a different "online" value, remove it and append the new value
            if data["serverID"] == status["serverID"] and data["online"] != status["online"]:
                self.inDatabase.remove(status)
            
        self.inDatabase.append({"serverID" : data["serverID"], "online" : data["online"]})

        #Change the key last_heard to timestamp
        data = {"serverID": data["serverID"], "timestamp": data["last_heard"], "online": data["online"]}
        #Insert the data into the database collection
        self.client.collection.insert_one(data)
        print(f"Send to database: {data}")