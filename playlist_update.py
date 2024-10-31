import json
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import base64
import supporting_scripts.config_tools as config_tools
import supporting_scripts.channel_tools as channel_tools
import re
def sendOff(msg):
    pgrm_signature = "playlist_update.py: "

    #opens the setup.json file
    # with open("setup.json", 'r') as info:
    #     data = json.load(info)
    #     playlist_link = (data['playlist_link']) 
    #     client_id = (data['client_id'])
    #     client_secret = (data['client_secret'])

    config_data = config_tools.config_data()
    client_id = (config_data['client_id'])
    client_secret = (config_data['client_secret'])
    playlist_channel = (config_data['pc'])

    open('spotify.json', 'w+').close() #clears old token info if there is any

    file1 = open("spotify.json", "a") #prepares file to be written to 

    file2 = open(".cache", "r+")#reads the cached file 
    rline2 = file2.readlines()
    for line in rline2:
        content = line

        file1.write(content)#writes the content into the json file
        
    file1.close()

    with open("spotify.json", 'r') as info: #reads the json file that was just written to 
        data = json.load(info)
        TOKEN = (data['access_token'])
        refresh_token = (data['refresh_token'])
        expires_at = (data['expires_at'])

    #This function keep the user from having to get a new token manually every hour
    def refesh_the_token(): 
            #This code was made possible by https://www.youtube.com/watch?v=-FsFT6OwE1A 
            #Notable timestamps 10:14, 40:25

            auth_client = client_id + ":" + client_secret
            auth_encode = 'Basic ' + base64.b64encode(auth_client.encode()).decode()

            headers = {
                'Authorization': auth_encode,
                }

            data = {
                'grant_type' : 'refresh_token',
                'refresh_token' : refresh_token
                }

            response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers) #sends request off to spotify

            if(response.status_code == 200): #checks if request was valid
                print(pgrm_signature + "The request to went through we got a status 200; Spotify token refreshed")
                response_json = response.json()
                new_expire = response_json['expires_in']
                print(pgrm_signature + "the time left on new token is: "+ str(new_expire / 60) + "min") #says how long
                return response_json["access_token"]
            else:
                print(pgrm_signature + "ERROR! The response we got was: "+ str(response))
                return TOKEN #last ditch to try and make it work if TOKEN varaible is still active

        
    now = int(time.time())#gets the current time 

    is_expried = expires_at - now < 60 #checks to see if the token is expired, is a boolean variable

    time_left = expires_at - now #finds out how much time is left on the token

    print(pgrm_signature + "the time left on orginial token is: "+ str(time_left / 60) + "min")
    if(is_expried): #if token is expried, get a new token with the refresh token
        sp = spotipy.Spotify(auth=refesh_the_token())#Refreshes the token from now on after 
    else:
        sp = spotipy.Spotify(auth=TOKEN) #creates object that interacts with spotify api; uses the first token generated; token only last 1 hour

    #chop playlist link into uri format
    #replace x, with y
    #Ex: line.replace(x,y)
    playlist_link = channel_tools.return_playlist_from_channel(sent_channel=msg.channel.id, playlist_channel=playlist_channel)
    #decide where song is going to go
    #return playlist link
    

    fline = playlist_link.replace("https://open.spotify.com/playlist/", "")#deletes first part of the link
    PLAYLISTID = fline.split("?", 1)[0]
    #PLAYLISTID = (fline.split("?si")[0]) #cuts off exess info from the link

    tracks = ["blankfaketrack"] #needed to have one space in the array
    file = open("uri.txt", "r") #open uri text file
    rline = file.readlines()
        
    #loops through the entire file and only adds one songs at a time to the array
    for line in reversed(list(rline)):
        if "spotify:track:" in line:
            tracks[0] = (line.strip()) #adds to the first element over and over again
            sp.playlist_add_items(playlist_id=PLAYLISTID, items=[tracks][0]) #adds to the actual playlist
    f = open('uri.txt', 'r+')
    f.truncate(0) 
    return "Playlist update request was sent and went through!"
 

#sendOff() used to debug file


def link_clean(link: str) -> str:
    # Split the link by "/" and take the last part (the ID)
    track_id = link.split('/')[-1]
    # Return the cleaned format
    return f"spotify:track:{track_id}"

def return_song_id(link: str) -> str:
    # Split by ':' to get the part after 'spotify:track:'
    track_id = link.split(':')[-1]
    # Split by '?' to remove any query parameters and keep only the ID
    track_id = track_id.split('?')[0]
    return track_id

def return_playlist_id(playlist_link):
    fline = playlist_link.replace("https://open.spotify.com/playlist/", "")#deletes first part of the link
    PLAYLISTID = fline.split("?", 1)[0]
    return PLAYLISTID

def cache_2_json():
    open('spotify.json', 'w+').close() #clears old token info if there is any

    file1 = open("spotify.json", "a") #prepares file to be written to 

    file2 = open(".cache", "r+")#reads the cached file 
    rline2 = file2.readlines()
    for line in rline2:
        content = line

        file1.write(content)#writes the content into the json file
        
    file1.close()


def refresh_the_token(client_id, client_secret):
    pgrm_signature = "playlist_update.py: "
    with open("spotify.json", 'r') as info: #reads the json file that was just written to 
        data = json.load(info)
        TOKEN = (data['access_token'])
        refresh_token = (data['refresh_token'])
        expires_at = (data['expires_at'])
            #This code was made possible by https://www.youtube.com/watch?v=-FsFT6OwE1A 
            #Notable timestamps 10:14, 40:25

        auth_client = client_id + ":" + client_secret
        auth_encode = 'Basic ' + base64.b64encode(auth_client.encode()).decode()

        headers = {
            'Authorization': auth_encode,
            }

        data = {
            'grant_type' : 'refresh_token',
            'refresh_token' : refresh_token
            }

        response = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers) #sends request off to spotify

        if(response.status_code == 200): #checks if request was valid
            print(pgrm_signature + "The request to went through we got a status 200; Spotify token refreshed")
            response_json = response.json()
            new_expire = response_json['expires_in']
            print(pgrm_signature + "the time left on new token is: "+ str(new_expire / 60) + "min") #says how long
            return response_json["access_token"]
        else:
            print(pgrm_signature + "ERROR! The response we got was: "+ str(response))
            return TOKEN #last ditch to try and make it work if TOKEN varaible is still active


def refesh_sp(): 
    pgrm_signature = "playlist_update.py: "
    #get default config data
    config_data = config_tools.config_data()
    client_id = (config_data['client_id'])
    client_secret = (config_data['client_secret'])
    


    #gets spotify.json data
    with open("spotify.json", 'r') as info: #reads the json file that was just written to 
        data = json.load(info)
        expires_at = (data['expires_at'])
        TOKEN = (data['access_token'])
    
    #converts our .cache file to a json for easier processing
    cache_2_json() #call this in the spotbot.py file main need to improve token

    now = int(time.time())#gets the current time 

    is_expried = expires_at - now < 60 #checks to see if the token is expired, is a boolean variable

    time_left = expires_at - now #finds out how much time is left on the token

    print(pgrm_signature + "the time left on orginial token is: "+ str(time_left / 60) + "min")
    if(is_expried): #if token is expried, get a new token with the refresh token
        sp = spotipy.Spotify(auth=refresh_the_token(client_id=client_id, client_secret=client_secret))#Refreshes the token from now on after 
    else:
        sp = spotipy.Spotify(auth=TOKEN) #creates object that interacts with spotify api; uses the first token generated; token only last 1 hour

    #return refreshed spotipy object
    return sp

#extracts a song from a message object
def song_link_extract(msg):
    # Regular expression to match Spotify links
    pattern = r"https?://open\.spotify\.com/track/\w+\?si=\w+"
    
    # Search for the pattern in the provided text
    match = re.search(pattern, msg.content)
    # Return the matched link if found, otherwise None
    song = match.group(0) if match else None
    
    return song

def sendOff2(msg):
    config_data = config_tools.config_data()
    playlist_channel = config_data['pc']
    pgrm_signature = "playlist_update.py: "
    
    #This function keep the user from having to get a new token manually every hour
    sp = refesh_sp()
    
    #gets the playlist link assoicated with a channel
    playlist_link = channel_tools.return_playlist_from_channel(sent_channel=msg.channel.id, playlist_channel=playlist_channel)

    #gets the link from the message
    song_link = song_link_extract(msg=msg)

    #cleans song link and returns uri
    song_uri = link_clean(link=song_link)
    
    #gets just the song id from the uri
    song_id = return_song_id(link=song_uri)

    #gets playlist id
    PLAYLISTID = return_playlist_id(playlist_link=playlist_link)

    tracks = [] #needed to have one space in the array
    tracks.append(song_id)
        
    #sends a list of tracks off
    sp.playlist_add_items(playlist_id=PLAYLISTID, items=tracks) #adds to the actual playlist

    return "Playlist update request was sent and went through!" + pgrm_signature
