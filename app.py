from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import json
from datetime import datetime

app = Flask(__name__)

app.secret_key = "SECRERET"
app.config['SESSION_COOKIE_NAME'] = 'Matts_Cookie'
TOKEN_INFO = "token_info"

with open('setup.json', 'r') as setupf:
    data = json.load(setupf)
    client_id = data['client_id']
    client_secret = data['client_secret']
    playlist_link = data['playlist_link']

@app.route('/')
def login():
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
        return redirect(url_for('login', _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])

    fline = playlist_link.replace("https://open.spotify.com/playlist/", "")
    PLAYLISTID = (fline.split("?si")[0])

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

    return render_template('index.html', num_songs=spotifyRQ1, timestamp=timestamp)

@app.route('/close_app', methods=['POST'])
def close_app():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/continue_setup', methods=['POST'])
def continue_setup():
    return render_template('setup.html')

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
        redirect_uri=url_for('redirectPage', _external=True),
        scope='playlist-modify-public user-library-read'
    )

if __name__ == '__main__':
    app.run(debug=True)
