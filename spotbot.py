from discord.ext import commands
import re
import sqlite3
import discord
from datetime import datetime
import json
import playlist_update
from os import path
import random
import calendar
import achievements
import aiohttp
import io
import database_tools

pgrm_signature = "spotbot.py: "

# Get any discord token in the DB
conn = sqlite3.connect('secrets.db')
cur = conn.cursor()

cur.execute('SELECT discord_token FROM setup')

TOKEN = cur.fetchone()

conn.close()


intents = discord.Intents.all()
intents.members = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)


@bot.event
async def on_ready():
    #Lets programmer know that the bot has been activated
    print(pgrm_signature + 'SpotifyBot: ON')


#This is the help command that lets the user know all of the avaliable commands that can be used 
@bot.command()
async def hlp(ctx):
    setup_info = database_tools.get_setup_info('secrets.db', ctx.message.guild.name)

    helpText = ("The commands for this bot go as follows: \n" + 
        "[!]sLink (gives the user the link to the spotify playlist) \n" + 
        "[!]grabPast (allows for the user to grab past songs sent in a chat, this can only be ran once) \n" +
        "[!]r (gives the user a random song from the playlist!) \n" +
        "[!]waves (generate Spotify's wave codes png image files.)\n")

    if int(setup_info[4]) == 1:
        helpText += ("[!]leaderboard (gives a leadearboard of all time highest contributing users) \n" +
            "[!]thismonth (gives a leaderboard of this months hightst contributing users) \n" +
            "[!]reactchamp (gives a leaderboard of this months most reacted contributed songs) \n")

    await ctx.reply(helpText +
            "When a user sends a messsage in this chat the bot will analyze that message, if it is a valid spotify link it will be placed into the playlist\n")
    

#gives the link set in the setup.json file
@bot.command()
async def sLink(ctx):
    playlist_array = database_tools.get_playlist_array('secrets.db', ctx.message.guild.name)
    
    for playlist in playlist_array:
        if int(playlist[1]) == ctx.channel.id:
            await ctx.reply(playlist[0])

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

# a request command to produce an all time leaderboard stats for the respective discord server 
@bot.command()
async def leaderboard(ctx):
    setup_info = database_tools.get_setup_info('secrets.db', ctx.message.guild.name)

    # Check if the leaderboard information is enabled via setup.json
    if setup_info[5] == 0: return False

    # Connect to the SQLite Database
    conn = sqlite3.connect('spotbot.db')
    cur = conn.cursor()

    # Get top 10 users and their number of songs added
    cur.execute("""
        SELECT sender_ID, COUNT(*) as song_count
        FROM songs
        GROUP BY sender_ID
        ORDER BY song_count DESC
    """)

    # Fetch all
    results = cur.fetchall()

    # Send the embed
    title="All Time Leaderboard"
    await sendLeaderBoardEmbed(ctx, results, title)

    # Close the connection
    conn.close()

# a request command to produce a leaderboard with this months stats for the respective discord server
@bot.command()
async def thismonth(ctx):
    setup_info = database_tools.get_setup_info('secrets.db', ctx.message.guild.name)
    
    # Check if the leaderboard information is enabled via setup.json
    if setup_info[4] == 0: return False

    # Connect to the SQLite Database
    conn = sqlite3.connect('spotbot.db')
    cur = conn.cursor()

    # Get the current year and month
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    # Get top 10 users and their number of songs added for the current month
    cur.execute("""
        SELECT sender_ID, COUNT(*) as song_count
        FROM songs
        WHERE strftime('%Y', timestamp) = ? AND strftime('%m', timestamp) = ?
        GROUP BY sender_ID
        ORDER BY song_count DESC
        LIMIT 10
    """, (str(current_year), f"{current_month:02d}"))

    # Fetch all
    results = cur.fetchall()

    # Send the embed
    title="This Months Stats"
    await sendLeaderBoardEmbed(ctx, results, title)

    # Close the connection
    conn.close()

# A request that produces a leaderboard with this months highest reacted songs
@bot.command()
async def reactChamp(ctx):
    # Get set up info and playlists
    setup_info = database_tools.get_setup_info('secrets.db', ctx.message.guild.name)

    # Check if the leaderboard information is enabled via setup.json
    if setup_info[4] == 0: return False

    # warn user this may take a while
    await ctx.send(f"Grabbing messages - this may take a while...")

    # Connect to SQLite Database
    conn = sqlite3.connect('spotbot.db') # create or connect to the database
    cur = conn.cursor()

    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    # Get top 10 users and their number of songs added for the current month
    cur.execute("""
        SELECT spotify_id, discord_message_id, sender_ID
        FROM songs
        WHERE strftime('%Y', timestamp) = ? AND strftime('%m', timestamp) = ?
    """, (str(current_year), f"{current_month:02d}"))

    message_ids = cur.fetchall()

    messages = []
    # loop through each message ID
    for msg_id in message_ids:
        try:
            message = await ctx.channel.fetch_message(msg_id[1])                        # Grab each message
            total_reactions = sum(reaction.count for reaction in message.reactions)     # grab the total amount of reacitons for respective message
            if total_reactions > 1:
                messages.append((message, total_reactions-1, msg_id[0], msg_id[2]))       # Add tuple of message, total reactions, and the spotify link
        except discord.NotFound:
            print(f"{pgrm_signature}: Message with ID {msg_id[1]} not found")
        except discord.Forbidden:
            print(f"{pgrm_signature}: Bot doesn't have permission to fetch message {msg_id[0]}")
        except discord.HTTPException:
            print(f"Failed to fetch message {msg_id[1]}")

    # Sort the results
    # sorted is fed messages, key=lambda (idk why), x[1] for the reaction count, 
    # and reverse true for descending orde. [:5] to get the top 5
    top_messages = sorted(messages, key=lambda x: x[1], reverse=True)[:5]

    # make and send the embed
    title = f"Reaction Champions for {calendar.month_name[current_month]}"
    embed = discord.Embed(title=title, color=0x1DB954)
    embed.description = "The top 5 highest reacted songs this month"

    loops = 1
    guild = ctx.guild
    for message in top_messages:
        # Get username
        member = guild.get_member(message[3])

        #will need username and link maybe?
        field_value = f"{message[1]} reaction(s) - "
        field_value += f"[Listen Here]({message[2]})"
        embed.add_field(name=f"{loops}. {member.display_name}", value=field_value, inline=False)
        loops += 1

    await ctx.send(embed=embed)

    conn.close()

# A request that produces a leaderboard with this months hight reacted songs local to the represented playlist
@bot.command()
async def localreactChamp(ctx):
    # Get set up info and playlists
    setup_info = database_tools.get_setup_info('secrets.db', ctx.message.guild.name)
    playlist_array = database_tools.get_playlist_array('secrets.db', ctx.message.guild.name)

    # Check if the leaderboard information is enabled via setup.json
    if setup_info[4] == 0: return False

    for playlist in playlist_array:
        if ctx.channel.id == int(playlist[1]):
            # warn user this may take a while
            await ctx.send(f"Grabbing messages - this may take a while...")

            # Connect to SQLite Database
            conn = sqlite3.connect('spotbot.db')
            cur = conn.cursor()

            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month

            playlist_link = database_tools.get_playlist_link('secrets.db', playlist[1])
            playlist_ID = getPlaylistID(playlist_link[0])

            # Get top 10 users and their number of songs added for the current month for the specified playlist
            cur.execute("""
                SELECT spotify_id, discord_message_id, sender_ID
                FROM songs
                WHERE strftime('%Y', timestamp) = ? AND strftime('%m', timestamp) = ? AND playlist_ID = ?
            """, (str(current_year), f"{current_month:02d}", playlist_ID,))

            message_ids = cur.fetchall()

            messages = []
            # loop through each message ID
            for msg_id in message_ids:
                try:
                    message = await ctx.channel.fetch_message(msg_id[1])                        # Grab each message
                    total_reactions = sum(reaction.count for reaction in message.reactions)     # grab the total amount of reacitons for respective message
                    if total_reactions > 1:
                        messages.append((message, total_reactions-1, msg_id[0], msg_id[2]))       # Add tuple of message, total reactions, and the spotify link
                except discord.NotFound:
                    print(f"{pgrm_signature}: Message with ID {msg_id[1]} not found")
                except discord.Forbidden:
                    print(f"{pgrm_signature}: Bot doesn't have permission to fetch message {msg_id[0]}")
                except discord.HTTPException:
                    print(f"Failed to fetch message {msg_id[1]}")

            # Sort the results
            # sorted is fed messages, key=lambda (idk why), x[1] for the reaction count, 
            # and reverse true for descending orde. [:5] to get the top 5
            top_messages = sorted(messages, key=lambda x: x[1], reverse=True)[:5]

            # make and send the embed
            title = f"Reaction Champions for {calendar.month_name[current_month]}"
            embed = discord.Embed(title=title, color=0x1DB954, url=playlist[0])
            embed.description = "The top 5 highest reacted songs this month"

            loops = 1
            guild = ctx.guild
            for message in top_messages:
                # Get username
                member = guild.get_member(message[3])

                #will need username and link maybe?
                field_value = f"{message[1]} reaction(s) - "
                field_value += f"[Listen Here]({message[2]})"
                embed.add_field(name=f"{loops}. {member.display_name}", value=field_value, inline=False)
                loops += 1

            await ctx.send(embed=embed)

            conn.close()

# Using the result from an SQL querey, an embed is created and sent
async def sendLeaderBoardEmbed(ctx, results, title):
    userIDs = [row[0] for row in results]
    usernames = {}
    guild = ctx.guild
    # For each user ID in the results get the username
    for userID in userIDs:
        try:
            member = guild.get_member(userID)
            if member is None:
                print(f"Debug: Fetching member {userID}")
                member = await guild.fetch_member(userID)
            
            # Attempt to get the display name, if not available get the name
            if member.display_name:
                usernames[userID] = member.display_name
            else:
                usernames[userID] = member.name
            
            print(f"{pgrm_signature}: Debug - User ID: {userID}, Name: {member.name}, Display name: {member.display_name}")

        except discord.NotFound:
            usernames[userID] = "Unknown User"

    # Create the embed
    embed = discord.Embed(title=title, color=0x1DB954)
    embed.description = "The top 10 users who have sent the most songs:"

    loops = 1

    for row in results:
        if loops != 10:
            discord_id, song_count = row
            username = usernames.get(discord_id, "Unknown")
            
            # Add the new information to the response
            # response += (f"\n{username:8s} | {song_count:15d}")
            embed.add_field(name=f"{loops}. {username}", value=f"{song_count} songs", inline=False)
            loops += 1
        else:
            # Only print the first 10
            break

    await ctx.send(embed=embed)

#This is to grab the past songs that have been sent to the channel
@bot.command()
async def grabPast(ctx):
    with open("setup.json", 'r') as setupf: #must reopen the file to check if flag has been updated
                    data = json.load(setupf)
                    grab_past_flag = (data['grab_past_flag'])

    client = discord.Client(intents=intents)

    if(grab_past_flag) == 1:
        await ctx.reply("grabPast has already been called. If this is a mistake please go to the setup.json file and set grab_past_flag to 0")
    else:
        # Alert the user
        await ctx.reply("Grabbing songs now please wait until FINISHED is sent")                
        await ctx.send("Grabbing & Flitering Past Messages (this could take a while).....")

        playlist_array = database_tools.get_playlist_array('secrets.db', ctx.message.guild.name)
        # 0 index is URL, 1 index is discord channelID

        # Loop through available playlists
        for playlist in playlist_array:
            # Clear the uri.txt file
            file1 = open("uri.txt", "w+")
            file1.close()

            # Get messages from each channel 
            messages = await fetch_message_history(playlist[1])

            # Loop through messages that contain spotify links
            word = "https://open.spotify.com/track"
            for msg in messages:
                if word in msg.content: # Only spotifiy links
                    dupCheck(msg, playlist[0])# send off the link and check to see if it is a duplicate                            
            
            # send off the spotifyIDs file to be uploaded to Spotify
            print(pgrm_signature + "Uri text file written to succesfully!\n")
            print(pgrm_signature + "Sending songs off to spotify")
            print(pgrm_signature + playlist_update.sendOff(playlist[0]))
    
        # send a success after the loop
        await ctx.send("Messages Grabbed, Process Complete, FINISHED" + "\n Here is the Spotify Link: " + playlist[0])
        
        update_gp_flag()
        print(f"{pgrm_signature}: Updated the grabpast flag")
        


@bot.event
async def on_message(msg):
    # Get the set up info and playlist array
    setup_info = database_tools.get_setup_info('secrets.db', msg.guild.name)
    playlist_array = database_tools.get_playlist_array('secrets.db', msg.guild.name)
    

    # Loop through available playlists
    for playlist in playlist_array:
    
        # If the link is sent into the chat specified
        if msg.channel.id == int(playlist[1]):
            # Record playlist link
            playlist_link = playlist[0]

            #once again, all the file work can be moved over to the dupCheck() function for single file handling
            strCheck = "https://open.spotify.com/track"

            if re.search(strCheck, msg.content):
                if not "The random song you got was:" in str(msg.content): # Without this it would catch all songs comand as a new link for some reason.
                    print(pgrm_signature + "Valid Spotify Link")

                    checkEmoji = "☑️"
                    rEmoji = "🔁" 

                    # Check to see if the song is duplicate, if not add it to the DB
                    test = dupCheck(msg, playlist_link)

                    #Decides what emoji to add based on if it is a duplicate or not
                    if(test == True):
                        await msg.add_reaction (rEmoji)
                    else:
                        # Once added to DB send to spotify to add to playlist
                        print(pgrm_signature + playlist_update.sendOff(playlist_link))
                        await msg.add_reaction(checkEmoji) #adds emoji when song is added to playlist

                        # Warn users that previous songs may not be accounted for as grabPast has NOT been called
                        if(setup_info[3] == 0):
                            await msg.reply("WARNING GRAB PAST FLAG IS STILL ZERO, IF THERE ARE NO PAST SONGS YOU NEED TO GRAB. SET THE GRAB PAST FLAG TO ZERO IN setup.json AND RESTART spotbot.py. THIS WILL CAUSE ERRORS ELSEWISE")
                        
                        # Check for acheivements (connect to db, get song count)
                        conn = sqlite3.connect('spotbot.db')
                        cur = conn.cursor()

                        cur.execute("SELECT COUNT(*) FROM songs WHERE playlist_ID = ?", (getPlaylistID(playlist_link),))
                        songs = cur.fetchone()[0]

                        # Every 10 songs check for achievements (For perfromance)
                        if (songs % 5 == 0 or songs == 69):
                            # Get the acheivement string (if any)
                            celebration = achievements.checkAchievement(songs, setup_info[3])

                            # Get duration achievement (if any)
                            duration = achievements.checkDurationAchievement(playlist_update.get_playlist_duration(playlist_link))

                            # If there is a celebration, send the message
                            if(celebration):
                                await msg.channel.send(celebration)
                            if(duration):
                                await msg.channel.send(duration)
                        
                        conn.close()

            else:
                # Print to the terminal that a message was recieved but it is NOT a spotify link
                print(pgrm_signature + "Not valid Spotify link")
        
            await bot.process_commands(msg)

            # Return True to show success and break from any loops
            return True



@bot.command()
async def waves(ctx, arg):
    playlist_array = database_tools.get_playlist_array('secrets.db', ctx.message.guild.name)
    # 0 index is URL, 1 index is discord channelID

    for playlist in playlist_array:
        # Command only functions within the global variable: discord_channel, specified in setup.json
        if ctx.channel.id == int(playlist[1]):
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

async def fetch_message_history(channel_ID):
    channel = bot.get_channel(channel_ID)
    if channel is None:
        print(f"Channel with ID {channel} not found.")
        try:
            channel = await bot.fetch_channel(channel_ID)
        except discord.errors.NotFound:
            print(f"Channel with ID {channel_ID} does not exist.")
        except discord.errors.Forbidden:
            print(f"Bot does not hav epermission to acces channel{channel_ID}")
    
    print(f"Channel found: {channel.name} (ID: {channel_ID}, Type: {type(channel)})")

    if not isinstance(channel, discord.TextChannel):
        print(f"Channel {channel_ID} is not a text channel.")
    
    try:
        messages = [message async for message in channel.history(limit=500000)]
        print(f"Successfully fetched {len(messages)} messages from channel {channel.id}")
    except discord.errors.Forbidden:
        print(f"Bot doesn't have permission to read message history in channel {channel.id}")
    except Exception as e:
        print(f"An error occurred while fetching history for channel {channel.id}: {e}")

    return messages


#checks for duplicates before sending songs off to uri.txt and recording in database
def dupCheck(msg, playlist_link):
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
    # Check if there is a song id in the specified playlist
    playlist_ID = getPlaylistID(playlist_link)
    cur.execute("SELECT spotify_ID FROM songs WHERE spotify_ID = ? AND playlist_ID = ?", (stripped,playlist_ID,))
    matches = cur.fetchone()

    # If a match is found
    if matches:
        print(pgrm_signature + 'String', string1, 'Found In song database')
        print(pgrm_signature + "DUPLICATE LINK FOUND, NOT ADDED TO PLAYLIST FILE")
        return True # EXIT and return true; this is infact a duplicate
    else: # If a match is not found
        print(pgrm_signature + 'String', string1 , 'Not Found')

        # Add the song ID into the database
        cur.execute("INSERT INTO songs (spotify_ID, playlist_ID, sender_ID, timestamp, discord_message_id) VALUES (?, ?, ?, ?, ?)", 
                    (stripped, playlist_ID, getSender(msg), getTimestamp(msg), getMessageID(msg)))
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
        file1 = open("uri.txt", "a")
    
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

def getPlaylistID(playlist_link):
    # Return the playlist ID
    return playlist_link.split('/')[-1].split('?')[0]

# Initialize the database if not created yet
# database_tools.initialize_database("spotbot.db", get_playlist_array)

# Refresh the token upon startup
playlist_update.startup_token_refresh()

bot.run(TOKEN[0])
