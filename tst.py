import json
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import base64
import supporting_scripts.config_tools as config_tools
import supporting_scripts.channel_tools as channel_tools
import discord
from discord.ext import commands


config_data = config_tools.config_data()
playlist_channel = config_data['pc']

channel_tools.return_playlist_from_channel(playlist_channel=playlist_channel, sent_channel=1300614868646367242)

