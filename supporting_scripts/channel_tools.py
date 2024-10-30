import json
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import base64
import supporting_scripts.config_tools as config_tools
import playlist_update as playlist_update
import discord
from discord.ext import commands


def bot_setup():
    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

    return bot

bot = bot_setup()
#function to check if bot started
#
#
# return startup

#function to check valid channels for songs if startup == true

def check_channels_on_boot(enabled=False, startup_flag=False, playlist_w_channel={}):
    if(enabled == True and startup_flag == True):
        #grab past like code needs to run

        print("Checking channels on boot")
    else:
        return


#grab past ish


async def search_past(ctx, enabled=False):
    if(enabled == True):
        word = "https://open.spotify.com/track"
        # await ctx.reply("Grabbing songs now please wait until FINISHED is sent")

        config_tools.logs("Grabbing past messages.....", log_file=r'logs/channel_tools.log')
        messages = [messages async for messages in ctx.history(limit=500000)] #If your bot is not reading all of your messages this number may have to be higher

        # await ctx.send("Spotbot is now checking past messages on boot. Grabbing & Flitering Past Messages(this could take a while).....")

        # to make it work with only one file, surprisingly all the playlist file handling is done in dupCheck()
        for msg in messages:
            if word in msg.content:
                sb.uritxt(msg.content)
                playlist_update.sendOff()
                await emojiCheck(msg)#checks to see if the correct emoji is on the message
        config_tools.logs("Grabbed past messages", log_file=r'logs/channel_tools.log')
        print("Past finished searching")

async def emojiCheck(msg):
    #checkEmoji = "☑️"
    checkEmoji = "💢"
    rEmoji = "🔁" 
    spotbot_emojis = rEmoji, checkEmoji
        # try:
    message = msg  
    if spotbot_emojis not in message.reactions:                                                        # Grab each message
        print(msg.content)
        await message.add_reaction (checkEmoji)
        #add songs to playlist

            # Add tuple of message, total reactions, and the spotify link
        # except discord.NotFound:
        #     print(f"{pgrm_signature}: Message with ID {msg_id[1]} not found")
        # except discord.Forbidden:
        #     print(f"{pgrm_signature}: Bot doesn't have permission to fetch message {msg_id[0]}")
        # except discord.HTTPException:
        #     print(f"Failed to fetch message {msg_id[1]}")
async def is_message_in_valid_channel(message, channels):
    if message.channel.id in channels:
        return True
    else:
        return False

async def return_channels(playlist_channel):
    channels = [] #makes an array of channels
    for item in playlist_channel:
        channel = int(playlist_channel[item]['channel']) #gets all channels from dict
        channels.append(channel) #appends channel to array
    return channels #retruns all channel w/o playlist links 

async def return_playlists(playlist_channel):
    playlists_links = [] #makes an array for all playlist items
    for item in playlist_channel:
        playlist = str(playlist_channel[item]['playlist'])
        playlists_links.append(playlist) #appends all playlist items to an array
    return playlists_links #retruns all playlist links w/o channel
    


#what channel has that playlist associated with it 
def return_playlist_from_channel(sent_channel, playlist_channel):
    for item in playlist_channel:
        channel = playlist_channel[item]['channel']
        if int(sent_channel) == int(channel):
            playlist_link = playlist_channel[item]['playlist']
    return playlist_link


