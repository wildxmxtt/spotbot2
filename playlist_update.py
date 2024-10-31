import json
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import base64
import database_tools

#with open("setup.json", 'r') as info:
#        data = json.load(info) 
#        client_id = (data['client_id'])
#        client_secret = (data['client_secret'])
pgrm_signature = "playlist_update.py: "

SECRET_DATABASE = 'setup.json'

def sendOff(playlist_link):
    # pgrm_signature = "playlist_update.py: "

    open('spotify.json', 'w+').close() #clears old token info if there is any

    file1 = open("spotify.json", "a") #prepares file to be written to 

    file2 = open(".cache", "r+")#reads the cached file 
    rline2 = file2.readlines()
    for line in rline2:
        content = line

        file1.write(content)#writes the content into the json file
        
    file1.close()

    data, TOKEN, refresh_token, expires_at = get_spotify_json()
        
    now = int(time.time())#gets the current time

    sp = get_spotify_api_object(now, data, TOKEN, refresh_token, expires_at) 

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


# This places in app.py because of the use of spotipy
# Returns the hours of songs in the playlist
def get_playlist_duration(playlist_link):
    # Set up authentication
    # client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    # sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist_ID = playlist_link.split('/')[-1].split('?')[0]

    data, TOKEN, refresh_token, expires_at = get_spotify_json()

        
    now = int(time.time())#gets the current time

    sp = get_spotify_api_object(now, data, TOKEN, refresh_token, expires_at) 

    # get all tracks from the playlist
    results = sp.playlist_items(playlist_ID)
    tracks = results['items']

    # Get all tracks if there are more than 100 in the playlist
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    
    # Sum the duration of all songs in miliseconds
    total_duration_ms = sum(track['track']['duration_ms'] for track in tracks if track['track'])

    # Convert milliseconds to hours
    duration_hours = total_duration_ms / (1000 * 60 * 60)
    
    return duration_hours

#sendOff() used to debug file

#This function keep the user from having to get a new token manually every hour
def refresh_the_token(data, TOKEN, refresh_token): 
    #This code was made possible by https://www.youtube.com/watch?v=-FsFT6OwE1A 
    #Notable timestamps 10:14, 40:25

    setupInfo = database_tools.get_setup_info(SECRET_DATABASE)

    auth_client = setupInfo['client_id'] + ":" + setupInfo['client_secret']
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
        
def get_spotify_json():
    with open("spotify.json", 'r') as info: #reads the json file that was just written to 
        data = json.load(info)
        TOKEN = (data['access_token'])
        refresh_token = (data['refresh_token'])
        expires_at = (data['expires_at'])

    return data, TOKEN, refresh_token, expires_at

def get_spotify_api_object(now, data, TOKEN, refresh_token, expires_at):
    is_expried = expires_at - now < 60 #checks to see if the token is expired, is a boolean variable

    time_left = expires_at - now #finds out how much time is left on the token

    print(pgrm_signature + "the time left on orginial token is: "+ str(time_left / 60) + "min")
    if(is_expried): #if token is expried, get a new token with the refresh token
        sp = spotipy.Spotify(auth=refresh_the_token(data, TOKEN, refresh_token))#Refreshes the token from now on after 
        
        # Now we must update the time that the token expires at
        # Open the file for reading first
        with open(".cache", 'r') as info:
            data = json.load(info)

        # Modify the data
        data['expires_at'] = now + 2600 # has smaller buffer than one hour

        # Open the file again, this time for writing
        with open(".cache", 'w') as info:
            json.dump(data, info, indent=4)
    else:
        sp = spotipy.Spotify(auth=TOKEN) #creates object that interacts with spotify api; uses the first token generated; token only last 1 hour

    return sp

# Method that retreves the tracks name and artist from spotify
def get_track_name_and_artist(trackID):
    data, TOKEN, refresh_token, expires_at = get_spotify_json()

    now = int(time.time())#gets the current time

    sp = get_spotify_api_object(now, data, TOKEN, refresh_token, expires_at)

    track = sp.track(trackID)
    artists = track['artists']
    # {track['artists']['name']

    return f"{track['name']} - {artists[0]['name']}"



# Token refresh method for startup
def startup_token_refresh():
    # Get old token information
    data, TOKEN, refresh_token, expires_at = get_spotify_json()
    
    # Refresh using the token info
    refresh_the_token(data, TOKEN, refresh_token)
