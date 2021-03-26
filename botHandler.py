# botHandler.py file manages the discordbot and handles it's events
# this script also starts up heartbeat_publisher and hearthbeat_subscriber
# authors: 1, 2 and Edwin Mursia

import os
from datetime import datetime

from cyberBot import botModules
from cyberBot import databaseRequest, connection

import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv


myclient = connection.dbClient

# loads environment variables from .env file, these are stored only locally!
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# if a command is added, also add it here
commands = ("!help", "!allstatuses", "!allservers",
            "!status", "!downtime", "!addserver", "!deleteserver")

# characters that bot should see as bad characters
restrictedCharacters = ('@','#','£','$','%','^','&','*','(',')','<','>','?','/','\\','|','}','{','~',';',']','[','¤','+',"'",'"','§','½')

# loading servers list from database, which is used to check correct id's
servers = []
for server in myclient.idcollection.find( {}, { "_id": 0 } ):
    servers.append(server)
print (f"Servers that are currently being tracked: \n{servers}")

# user roles that can use commands to call bot
GreaterRoles = ("Admin")
LesserRoles = ("Admin", "Tester")

# creating connection to discord as a client
client = discord.Client()

# EVENT HANDLERS GO HERE

# confirms the connection
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )


# responds to certain messages sent by users
@client.event
async def on_message(message):
    if message.author == client.user:
            return

# if the user inputs "!" in the beginning of a string, bot sees it as a command
    if (message.content[0] == "!"):
        currentMessage = message.content.lower()
        splittedMessage = currentMessage.split(" ")
        command = splittedMessage[0]

        if any(char in currentMessage for char in restrictedCharacters):
            await message.channel.send("```Bad characters! Use only alphabets and numbers```")

        # if command found in commands, execute one of these
        elif command in commands:

            #Only user with an Admin-role can use these commands
            if GreaterRoles in str(message.author.roles):

                if currentMessage == '!allservers':
                    returnList = []
                    for server in servers:
                        returnList.append(server)
                    #sorts servers list by id number
                    returnList = sorted(returnList, key = lambda i: i["serverID"])
                    answer = ""
                    for dic in returnList:
                        answer += str(dic)
                        answer += " \n"  

                    await message.channel.send(f"```{answer}```" )
                
                if currentMessage == '!allstatuses':
                    allCurrentStatuses = botModules.getAllCurrentStatuses()
                    allCurrentStatuses = sorted(allCurrentStatuses, key = lambda i: i["serverID"])
                    answer = ""
                    for status in allCurrentStatuses:
                        serverID = status["serverID"]
                        timestamp = status["timestamp"]
                        online = status["online"]
                        answer += f"Status for server {serverID}: at {timestamp} {online} \n"
                        
                    await message.channel.send(f"```{answer}```")

                if splittedMessage[0] == '!status':                
                    try: 
                        serverID = int(splittedMessage[1])
                        response = botModules.getCurrentStatus(serverID)           
                        await message.channel.send(response)
                    except:
                        await message.channel.send("```Invalid argument: needs to be integer and within server ID range, check '!allservers' for correct ID numbers```")
          
                if splittedMessage[0] == '!downtime':
                    notValid = True
                    while notValid:
                        try: 
                            serverID = int(splittedMessage[1])
                            notValid = False
                        except:
                            await message.channel.send("```Argument needs to be integer and within server ID range, check '!allservers' for correct ID numbers```")  

                        try:
                            startDate = botModules.convertToEpoch(splittedMessage[2])
                            endDate = botModules.convertToEpoch(splittedMessage[3])
                            notValid = False
                        except:
                            await message.channel.send("```Invalid dateformat: use (dd.mm.YYYY-HH:MM:SS)```")

                        if notValid == False:
                            response = databaseRequest.getDownTimes(serverID, startDate, endDate)
                            for line in response:
                                await message.channel.send(f"```{line}```")
                                #await message.channel.send(file=discord.File('allRecords.txt'))
                        break
              
            #Commands everyone can use
            if LesserRoles[0] or LesserRoles[1] in str(message.author.roles):

                if currentMessage == '!help':
                    response = botModules.showCommands()
                    await message.channel.send(response)

            #Add a new server to servers database
                if splittedMessage[0] == '!addserver':
                    try:
                        name = str(splittedMessage[1])
                    except:
                        await message.channel.send("```Please enter arguments with the command```")
                    try:
                        serverID = int(splittedMessage[2])
                    except:
                        await message.channel.send("```2nd argument needs to be integer and that ID cannot exist already``")

                    idsFound = 0
                    for server in servers:
                        if server["serverID"] == serverID:
                            idsFound += 1
                        
                    if idsFound == 0 and isinstance(serverID, int):
                        timestamp = datetime.now()
                        currentTime = timestamp.strftime('%d.%m.%Y %H:%M:%S') 
                        try:
                            # Sending new server with id to data storage
                            botModules.addServer(serverID)
                            # Saving new server to servers list
                            servers.append({"name": name, "serverID": serverID})
                            # Sending new server to servers collection on database
                            myclient.idcollection.insert_one({"name": name, "serverID": serverID})                        
                            print(f'Creation of "{name}" with ID {serverID} by user {message.author} was successful at {currentTime}')
                            await message.channel.send(f'```Creation of "{name}" with ID of {serverID} was successful```')
                        except:
                            await message.channel.send("```Something went wrong, could not add new server```")                   
                    else:
                        await message.channel.send(f"```Server with ID: {serverID} already exists```")

            #Deletes a server from servers database
                if splittedMessage[0] == '!deleteserver':
                    try:
                        serverID = int(splittedMessage[1])
                    except:
                        await message.channel.send(f"```Argument needs to be integer and that ID needs to belong to a server```")
                    
                    idsFound = 0 
                    for server in servers:
                        if server["serverID"] == serverID:
                            idsFound += 1
                            try:
                                botModules.deleteServer(serverID)
                                servers.remove(server)
                                deleteCommand = {"serverID": serverID}
                                result = myclient.idcollection.delete_one(deleteCommand)
                                print("Delete successful:", result.acknowledged)
                                timestamp = datetime.now()
                                currentTime = timestamp.strftime('%d.%m.%Y %H:%M:%S')
                                if result.acknowledged == True:
                                    print(f'```Server with an id of {serverID} was successfully deleted by {message.author} at {currentTime}```')
                                    await message.channel.send(f'```Server with an id of {serverID} was successfully deleted```')
                            except:
                                 await message.channel.send("```Error, couldn't delete from database```")

                    if idsFound == 0:
                        await message.channel.send(f"```No server with id of {serverID} exists```")                    
        
        # if user inputs invalid command, bot will show all of the commands
        else:
            print ("This wasn't a command. Showing help message for all the commands")
            response = botModules.showCommands()
            await message.channel.send(f"This is not a command. Try one of these instead:\n{response}")

client.run(TOKEN)