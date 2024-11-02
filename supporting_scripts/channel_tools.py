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
pgrm_signature = "channel_tools"

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


async def search_past(ctx, enabled=False, channel=""):
    if(enabled == True):
        word = "https://open.spotify.com/track"
        # await ctx.reply("Grabbing songs now please wait until FINISHED is sent")

        config_tools.logs("Grabbing past messages.....", log_file=r'logs/channel_tools.log')
        messages = [messages async for messages in ctx.history(limit=500000)] #If your bot is not reading all of your messages this number may have to be higher

        # await ctx.send("Spotbot is now checking past messages on boot. Grabbing & Flitering Past Messages(this could take a while).....")

        # to make it work with only one file, surprisingly all the playlist file handling is done in dupCheck()
        for msg in messages:
            try:
                if word in msg.content:
                    # sb.uritxt(msg.content)
                    has_spotbot_emoji = await emojiCheck(msg)#checks to see if the correct emoji is on the message
                    #if it dose not have a spotbot emoji, assume false and attempt to add: NOTE add later check to verify in db that song has NOT been added
                    if has_spotbot_emoji == False:
                            try:
                                playlist_update.sendOff2(msg=msg)
                            except Exception as e:
                                config_tools.logs(message="Error when sending song off to spotify: " + str(e), log_file=r'logs/error.log')       
                            try:
                                #if the emoji add fails
                                await addEmoji(msg=msg)
                            except Exception as e:
                                config_tools.logs(message="Error while adding emoji to un-captured message (bot most likey attempted to update to many messages with emojis, and is in timeout by discord)")
            #if the emoji check fails
            except discord.NotFound:
                config_tools.logs(message=f"{pgrm_signature}: Message with ID {msg.id} not found", log_file=r'logs/error.log')
            except discord.Forbidden:
                config_tools.logs(message=f"{pgrm_signature}:  Bot doesn't have permission to fetch message {msg.id}", log_file=r'logs/error.log')
            except discord.HTTPException:
                config_tools.logs(message=f"{pgrm_signature}: Failed to fetch message {msg.id}", log_file=r'logs/error.log')
            except Exception as e:
                config_tools.logs(message="Error whist fetching emoji: " + str(e), log_file=r'logs/error.log')
                
    
        config_tools.logs("Grabbed past messages", log_file=r'logs/channel_tools.log')
        print("Past finished searching for channel " + str(channel))


def msg_reactions_list(msg_reactions):
    emoji_list = []
    for item in msg_reactions:
        emoji = item.emoji
        emoji_list.append(emoji)
    
    return emoji_list


def emoji_list_match(list1, list2):
    # Check if there is any intersection between the two lists
    if set(list1).intersection(set(list2)):
        return True
    else:
        return False

async def addEmoji(msg, checkEmoji = "☑️"):
    print(msg.content)
    await msg.add_reaction (checkEmoji)

async def emojiCheck(msg):
    checkEmoji = "☑️"
    #checkEmoji = "💢"
    rEmoji = "🔁" 
    spotbot_emojis = [rEmoji, checkEmoji]
        # try:
    emoji_list = msg_reactions_list(msg_reactions=msg.reactions)
    #if false that means spotbot has not scanned the message before
    spotbot_emoji_flag = emoji_list_match(spotbot_emojis, emoji_list)
    if spotbot_emoji_flag == False:                                                        # Grab each message
        return False
    else: 
        return True
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


