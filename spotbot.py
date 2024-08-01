from discord.ext import commands
import re
import sqlite3
import discord
from datetime import datetime
import json
import playlist_update
from os import path
import random
import aiohttp
import io

pgrm_signature = "spotbot.py: "

with open("setup.json", 'r') as setupf:
    data = json.load(setupf)
    TOKEN = (data['discord_token'])
    client_id = (data['client_id'])
    client_secret = (data['client_secret'])
    playlist_link = (data['playlist_link'])
    grab_past_flag = (data['grab_past_flag'])
    discord_channel = (data['discord_channel'])


intents = discord.Intents.all()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)


@bot.event
async def on_ready():
    #Lets programmer know that the bot has been activated
    print(pgrm_signature + 'SpotifyBot: ON')


#This is the help command that lets the user know all of the avaliable commands that can be used 
@bot.command()
async def hlp(ctx):
    await ctx.reply("The commands for this bot go as follows: \n" + 
    "[!]sLink (gives the user the link to the spotify playlist) \n" + 
    "[!]grabPast (allows for the user to grab past songs sent in a chat, this can only be ran once) \n" +
    "[!]r (gives the user a random song from the playlist!) \n" +
    "[!]waves (generate Spotify's wave codes png image files.)\n" +
    "When a user sends a messsage in THIS CHAT the bot will analyis that message, if it is a valid spotify link it will be placed into the playlist\n" 
    
    )

#gives the link set in the setup.json file
@bot.command()
async def sLink(ctx):
     await ctx.reply(playlist_link)

#a request command to give the user back a random song from the playlist 
@bot.command()
async def r(ctx): 
    # Connect to the SQLite Database
    conn = sqlite3.connect('spotbot.db')
    cur = conn.cursor()

    # Get the number of total songs in the playlist
    cur.execute('SELECT COUNT(*) FROM songs')
    count = cur.fetchone()[0]

    print(f"There are {count} song IDs in the songs table.")

    # Get all spotify_IDs from the songs table
    cur.execute('SELECT spotify_ID FROM songs')
    spotify_ids = [row[0] for row in cur.fetchall()]

    # if there are songs
    if spotify_ids:
        # get a random id
        random_song = random.choice(spotify_ids)
        print(f"The random song you got was: {random_song}")
        await ctx.reply(f"The random song you got was: {random_song}")
    else: # if there are no songs
        print(f"There are no songs yet.")
        await ctx.reply("There are no songs yet. A random song cannot be retrieved.")

    # Close the connection
    conn.close()



#This is to grab the past songs that have been sent to the channel
@bot.command()
async def grabPast(ctx):
    with open("setup.json", 'r') as setupf: #must reopen the file to check if flag has been updated
        data = json.load(setupf)
        grab_past_flag = (data['grab_past_flag']) 

    # Grab past is intended to be called once, this is a catch to not re-compute old messages that
    #   have already been recorded
    if(grab_past_flag) == 1: 
        await ctx.reply("grabPast has already been called. If this is a mistake please go to the setup.json file and set grab_past_flag to 0")
    else:
        word = "https://open.spotify.com/track"
        await ctx.reply("Grabbing songs now please wait until FINISHED is sent")

        # Grab messages from the channel
        messages = [messages async for messages in ctx.channel.history(limit=500000)] #If your bot is not reading all of your messages this number may have to be heigher
        await ctx.send("Grabbing & Flitering Past Messages (this could take a while).....")

        # to make it work with only one file, surprisingly all the SQL is handled in dupCheck()
        # Loop through each message
        for msg in messages:
            if word in msg.content: # Only spotifiy links
                dupCheck(msg)# send off the link and check to see if it is a duplicate
                # If the song is not a duplicate
                    
        
         # send off the spotifyIDs file to be uploaded to Spotify
        print(pgrm_signature + playlist_update.sendOff())
        await ctx.send("Messages Grabbed, Process Complete, FINISHED" + "\n Here is the Spotify Link: " + playlist_link)
        
        update_gp_flag()
        print("Updated the grabpast flag")
        


@bot.event
async def on_message(msg):
    #grabs the discord channel specified in setup.json
    if msg.channel.id == discord_channel:
    #once again, all the file work can be moved over to the dupCheck() function for single file handling
        strCheck = "https://open.spotify.com/track"

        if re.search(strCheck, msg.content):
            if not "The random song you got was:" in str(msg.content): # Without this it would catch all songs comand as a new link for some reason.
                print(pgrm_signature + "Valid Spotify Link")

                checkEmoji = "☑️"
                rEmoji = "🔁" 

                # Check to see if the song is duplicate, if not add it to the DB
                test = dupCheck(msg)

                #Decides what emoji to add based on if it is a duplicate or not
                if(test == True):
                    await msg.add_reaction (rEmoji)
                else:
                    # Once added to DB send to spotify to add to playlist
                    print(pgrm_signature + playlist_update.sendOff())
                    await msg.add_reaction(checkEmoji) #adds emoji when song is added to playlist

                    # Warn users that previous songs may not be accounted for as grabPast has NOT been called
                    if(grab_past_flag == 0):
                        await msg.reply("WARNING GRAB PAST FLAG IS STILL ZERO, IF THERE ARE NO PAST SONGS YOU NEED TO GRAB. SET THE GRAB PAST FLAG TO ZERO IN setup.json AND RESTART spotbot.py. THIS WILL CAUSE ERRORS ELSEWISE")

        else:
            # Print to the terminal that a message was recieved but it is NOT a spotify link
            print(pgrm_signature + "Not valid Spotify link")
    
        await bot.process_commands(msg)



@bot.command()
async def waves(ctx, arg):
    # Command only functions within the global variable: discord_channel, specified in setup.json
    if ctx.channel.id == discord_channel:
        try:
            # Regex to ensure argument passed to command is acceptable
            uri_regex = r'https://open.spotify.com/track/(.+?)\?si='
            wave_uri = re.search(uri_regex, arg)
            # Format URL string for async request
            wave_url = 'https://scannables.scdn.co/uri/plain/png/000000/white/640/spotify:track:%s' % (wave_uri.group(1))
            # Async request for a response from variable: wave_url
            async with aiohttp.ClientSession() as wave_session:
                async with wave_session.get(wave_url) as wave_resp:
                    # Catch "unsuccessful" (not 200) response status
                    if wave_resp.status != 200:
                        return await ctx.send('Wavecode not found')
                    wave_img = io.BytesIO(await wave_resp.read())
            # Sends image structured in Bytes as a discord.File in the channel
            await ctx.send(file=discord.File(wave_img, '%s_wavecode.png' % (wave_uri.group(1))))

        # Catching unexpected errors
        except Exception as err:
            print(pgrm_signature + "Error occurred -> %s" % err)


#checks for duplicates before sending songs off to uri.txt and recording in database
def dupCheck(msg):
    string1 = msg.content
    
    # opening a text files (new)
    conn = sqlite3.connect('spotbot.db')
    cur = conn.cursor()

    # Separate the string supplied to just the spotify ID
    # are the same song:
    # https://open.spotify.com/track/2XgTw2co6xv95TmKpMcL70?si=dbe7fd4a016344ec
    # https://open.spotify.com/track/2XgTw2co6xv95TmKpMcL70?si=8fe74b50ad804b52
    sep = '?'
    stripped = string1.split(sep, 1)[0]

    # Attempt to select spotify_ID
    # input sanitization - https://realpython.com/prevent-python-sql-injection/
    #cur.execute("SELECT spotify_ID FROM songs WHERE spotify_ID = ?'," (stripped, )) # sanitized input?
    cur.execute("SELECT spotify_ID FROM songs WHERE spotify_ID = ?", (stripped,))
    matches = cur.fetchone()

    # If a match is found
    if matches:
        print(pgrm_signature + 'String', string1, 'Found In song database')
        print(pgrm_signature + "DUPLICATE LINK FOUND, NOT ADDED TO PLAYLIST FILE")
        return True # EXIT and return true; this is infact a duplicate
    else: # If a match is not found
        print(pgrm_signature + 'String', string1 , 'Not Found')

        # Add the song ID into the database
        cur.execute("INSERT INTO songs (spotify_ID, sender_ID, timestamp, discord_message_id) VALUES (?, ?, ?, ?)", 
                    (stripped, getSender(msg), getTimestamp(msg), getMessageID(msg)))
        conn.commit()
    
    # Add to the uri.txt file to be sent off
    uritxt(msg.content)

    # Close the connection to the database
    conn.close()

def uritxt(link):
    #opens up the setup.json file
    with open("setup.json", 'r') as setupf:
        data = json.load(setupf)
        grab_past_flag = (data['grab_past_flag']) #this will check if the grab_past_flag has been updated

    print(pgrm_signature + "Writting to uri.txt..... \n")
    
    # Ensure the link is computed as a str
    song = str(link)

    if(grab_past_flag == 0):
        # new code
        print("WARNING GRAB PAST FLAG IS SET TO ZERO, MAKE SURE THIS IS SET TO 1 IF YOU DONT HAVE ANY SONGS YOU NEED TO GET FROM THE PAST")
        print(pgrm_signature + "Writting to uri.txt.....: \n")

        # connect to the database
        conn = sqlite3.connect('spotbot.db')
        cur = conn.cursor()

        # Select all spotify IDs
        cur.execute("Select spotify_ID FROM songs")
        rline = cur.fetchall() # retreive all spotify IDs and store in readlines

        # Prepare to write the spotify IDs to the uri.txt file
        file1 = open("uri.txt", "w+")
    
        # Loop through each spotify ID
        for line in rline:
            # Convert tuple to string if necessary, sometimes we receive a string
            if isinstance(line, tuple):
                line = line[0] # Take the first element of the tuple (spotifyID)

            # Adds expected format to begingin of the spotify ID and writes to the file
            formattedLine = line.replace("https://open.spotify.com/track/", "spotify:track:")

            # Cuts off exess info from the uri and writes it to the file
            file1.write(formattedLine.split("?si")[0] + "\n")

        # Send status, close the connection and file
        print(pgrm_signature + "uri.txt has been written to")
        file1.close()
        conn.close()
        
    else:
        file1 = open("uri.txt", "w+")

        # Changing to the format expected
        formattedLine = song.replace("https://open.spotify.com/track/", "spotify:track:")
        formattedLine = formattedLine.split("?", 1)[0] # removing all contents regarding session ID
        
        # Writes URI to the file
        file1.write(formattedLine + "\n")
        print(f"These have been written to the uri.txt file")

        file1.close()

        print(pgrm_signature + "Uri text file written to succesfully!\n")
        print(pgrm_signature + "Sending songs off to spotify")
    
def update_gp_flag(): 
 ###Update grab_past_flag#####
    filename = "setup.json"
    dictObj = []

    # Check if file exists
    if path.isfile(filename) is False:
        raise Exception("File not found")
    
    # Read JSON file
    with open(filename) as fp:
        dictObj = json.load(fp)
    
        # "grab_past_flag" : 0
        dictObj.update({"grab_past_flag": 1})
    
        with open(filename, 'w') as json_file:
            json.dump(dictObj, json_file, 
                        indent=4,  
                        separators=(',',': '))
    
        print(pgrm_signature + 'Successfully updated setup.json')
    
# Get the message sender data
def getSender(msg):
    # get the sender id
    senderId = msg.author.id

    # return the sender ID to be used in dupCheck to be recorded in the songs playlist
    return senderId

# returns the formatted time stamp
def getTimestamp(msg):
    # Get the timestamp from the message
    timestamp = msg.created_at

    # Format the timestamp as a string
    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # return the sender ID to be used in dupCheck to be recorded in the songs playlist
    return formatted_timestamp

# Returns the message ID of a msg
def getMessageID(msg):
    # Get the ID for the message on discord
    message_id = str(msg.id)

    # return the sender ID to be used in dupCheck to be recorded in the songs playlist
    return message_id

bot.run(TOKEN)
