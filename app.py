from flask import Flask, request, url_for, session, redirect, render_template, flash
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import json
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

app.secret_key = "SECRERET"
app.config['SESSION_COOKIE_NAME'] = 'Matts_Cookie'
TOKEN_INFO = "token_info"

playlist_array = []

#gets info from setup file
with open('setup.json', 'r') as setupf:
    data = json.load(setupf)
    client_id = (data['client_id'])
    client_secret = (data['client_secret'])
    playlists = (data['playlists'])

    for playlist in playlists:
        # Extract playlist attributes
        playlist_name = playlist['playlist_name']
        playlist_link = playlist['playlist_link']
        discord_channel = playlist['discord_channel']
        
        # Add to playlist array
        playlist_array.append([playlist_name, playlist_link, discord_channel])


#do this function above twice

#a session is where we store data about a users session, prevents reloggin in
#setting up endpoints


@app.route('/')
def index():
    num_songs = '(if you are reading this, it means you have to click the "Link Spotify" Button)'
    timestamp = ''
    return render_template('index.html', num_songs=num_songs, timestamp=timestamp)

@app.route('/link_spotify')
def link_spotify():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info

    return redirect(url_for('getTracks', _external=True))

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for('index'))

    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Using the first playlist from JSON to get the link
    first_playlist = playlist_array[0]
    fline = first_playlist[1].replace("https://open.spotify.com/playlist/", "")#deletes first part of the link
    PLAYLISTID = (fline.split("?si")[0]) #cuts off exess info from the link
    print(PLAYLISTID)

    print("SPOTIFY REQUEST WENT THROUGH!!!! ")

    all_songs = []
    count = 0
    while True:
        items = sp.playlist_items(playlist_id=PLAYLISTID, limit=50, offset=count * 50)['items']
        count += 1
        all_songs += items
        if len(items) < 50:
            break
    
    spotifyRQ1 = str(len(all_songs))
    timestamp = str(datetime.now())
    print("The amount of songs in the playlist are: " + spotifyRQ1)
    print("TIMESTAMP: " + timestamp)
    
    open('uri.txt', 'w+').close()
    print("uri.txt has been reset")
    spotifyRQ1 = spotifyRQ1 + " SUCCESS Spotify has been linked!"
    return render_template('index.html', num_songs=spotifyRQ1, timestamp=timestamp)

@app.route('/close_app', methods=['POST'])
def close_app():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/continue_setup', methods=['POST'])
def continue_setup():
    return render_template('setup.html', installed_features=data['installed_features'])

@app.route('/advanced_setup', methods=['GET', 'POST'])
def advanced_setup():
    if request.method == 'POST':
        data['client_id'] = request.form['client_id']
        data['client_secret'] = request.form['client_secret']
        data['discord_token'] = request.form['discord_token']
        data['playlist_links'] = request.form['playlist_links']
        data['discord_channels'] = request.form['discord_channels']
        
        # Update features based on checkboxes
        for feature in data['installed_features']:
            data['installed_features'][feature] = feature in request.form.getlist('features')
        
        # Save the updated configuration to setup.json
        with open('setup.json', 'w') as setupf:
            json.dump(data, setupf)
        
        flash('Setup file updated!')
        return redirect(url_for('advanced_setup'))
    
    return render_template('advanced_setup.html', **data)

@app.route('/save_setup', methods=['POST'])
def save_setup():
    client_id = request.form['client_id']
    client_secret = request.form['client_secret']
    discord_token = request.form['discord_token']
    playlist_links = request.form['playlist_links']
    discord_channels = request.form['discord_channels']

    data['client_id'] = client_id
    data['client_secret'] = client_secret
    data['discord_token'] = discord_token 
    data['playlist_links'] = playlist_links
    data['discord_channels'] = discord_channels

    with open('setup.json', 'w') as setupf:
        json.dump(data, setupf)
    
    flash('Setup file updated!')
    return redirect(url_for('setup'))

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expried = token_info['expires_at'] - now < 60

    if is_expried:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
    client_id,
    client_secret,
    redirect_uri = url_for('redirectPage', _external=True), # Auto gernates this in the url_for http://localhost:5000/callback
    scope = 'playlist-modify-public user-library-read' )   

