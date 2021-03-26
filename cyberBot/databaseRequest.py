# requests data based on arguments from the status_database
# contains functions that botHandler.py calls for
# authors: 1, 2 and Edwin Mursia

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

import os
from dotenv import load_dotenv

import datetime
import time, os
import json

from cyberBot import connection

myclient = connection.dbClient

# gets records from database depending on a given timescale and server id number
def getDownTimes(serverID, startDate, endDate):
    serverID = int(serverID)
    start = int(startDate)
    end = int(endDate)
    finalDownTimes = []

    allRecords = []
    recordCount = 0
    currentStatus = ""

    #write to text file if there are too many records between given times
    def writeToFile():
        print ("Too many records, wrote into textfile")
        file1 = open("allRecords.txt", "w")
        file1.write(json.dumps(allRecords))
        file1.close()

    for record in myclient.collection.find( {"serverID": serverID, "timestamp": { "$gte": start, "$lt": end } }, { "_id": 0 } ):
        if record["online"] != currentStatus:
            currentStatus = record["online"]
            allRecords.append(record)
            recordCount += 1

    if recordCount == 0:
        answer = ["no status changes on a given time scale"]
        print("no records found")
        return answer
    
    elif recordCount >= 1:
        print (allRecords)

        #converting timestamps to dates
        for downtime in allRecords:
            downtime["timestamp"] = convertToDate(downtime["timestamp"])

        # if 1st online value is true, mark server as down from given starttime to 1st record which changed online value to true
        if allRecords[0]["online"] == True:
            startDict = {}
            start = convertToDate(start)
            startDict["serverID"] = serverID
            startDict["timestamp"] = start
            finalDownTimes.append(startDict)

            for dic in allRecords:
                finalDownTimes.append(dic)

            #if last online value is false, conclude that the last downtime is from this value to end of the given endtime
            if allRecords[-1]["online"] == False:
                endDict = {}
                end = convertToDate(end)
                endDict["serverID"] = serverID
                endDict["timestamp"] = end
                finalDownTimes.append(endDict)

            counter = 0
            returnableList = []
            for downStart in finalDownTimes:
                if counter >= len(finalDownTimes):
                    break
                firstTime = finalDownTimes[0 + counter]["timestamp"]
                secondTime = finalDownTimes[1 + counter]["timestamp"]
                counter += 2
                answer = (f'Server {serverID} has been down from {firstTime} to {secondTime}')
                returnableList.append(answer)

            if recordCount <= 10:
                return (returnableList)
            elif recordCount > 10:
                answer = writeToFile()   
                return answer


        # check if the 1st online value is false
        elif allRecords[0]["online"] == False:
            for dic in allRecords:
                finalDownTimes.append(dic)

            #if last online value is false, conclude that the last downtime is from this value to end of the given endtime
            if allRecords[-1]["online"] == False:
                endDict = {}
                end = convertToDate(end)
                endDict["serverID"] = serverID
                endDict["timestamp"] = end
                finalDownTimes.append(endDict)

            counter = 0
            returnableList = []
            for downStart in finalDownTimes:
                if counter >= len(finalDownTimes):
                    break
                firstTime = finalDownTimes[0 + counter]["timestamp"]
                secondTime = finalDownTimes[1 + counter]["timestamp"]
                counter += 2
                answer = (f'Server {serverID} has been down from {firstTime} to {secondTime}')
                returnableList.append(answer)

            if recordCount <= 10:
                return (returnableList)
            elif recordCount > 10:
                answer = writeToFile()   
                return answer

def convertToDate(timestamp):
    newDate = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(timestamp))
    return newDate 