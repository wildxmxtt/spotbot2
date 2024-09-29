from flask import Flask, request, url_for, session, redirect, render_template, flash
import spotipy, sqlite3
from spotipy.oauth2 import SpotifyOAuth
import time, os
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
import database_tools as dbt

app = Flask(__name__)

app.secret_key = "SECRERET"
app.config['SESSION_COOKIE_NAME'] = 'Matts_Cookie'
TOKEN_INFO = "token_info"

playlist_array = []

# Sets up our secret information into the application from secrets.db
secret_setup_info = dbt.get_secret_setup_info_dict(r'databases\secrets.db')
if secret_setup_info is not None:
    client_id = secret_setup_info['client_id']
    client_secret = secret_setup_info['client_secret']

# Sample installed features setup
# This can later be populated from an external source or form submission in the future
installed_features = {
    "Spotify Integration": True,
    "Discord Integration": True,
    "Track Playlist Milestones": False,
    "Track Song Plays": False,
}

@app.route('/')
def index():
    num_songs = '(if you are reading this, it means you have to click the "Link Spotify" Button)'
    timestamp = ''
    return render_template('index.html', num_songs=num_songs, timestamp=timestamp)

@app.route('/view_database/<db_name>', methods=['GET', 'POST'])
def view_database(db_name):
    db_folder = "databases/"
    db_path = f"{db_folder}{db_name}.db"
    db_files = [f.split('.')[0] for f in os.listdir(db_folder) if f.endswith('.db')]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]

    table_data = None
    column_names = None
    selected_table = None

    if request.method == 'POST':
        selected_table = request.form['table']
        cursor.execute(f"PRAGMA table_info({selected_table})")
        column_names = [info[1] for info in cursor.fetchall()]
        cursor.execute(f'SELECT * FROM {selected_table}')
        table_data = cursor.fetchall()

    conn.close()

    return render_template(
        'database_view.html', 
        db_files=db_files, 
        selected_db=db_name, 
        tables=tables, 
        selected_table=selected_table, 
        data=table_data, 
        column_names=column_names
    )
@app.route('/save_advanced_setup', methods=['POST'])
def save_advanced_setup():
    setup_data = {
        'client_id': request.form['client_id'],
        'client_secret': request.form['client_secret'],
        'discord_token': request.form['discord_token'],
        'playlist_link': request.form['playlist_links'],
        'discord_channel': request.form['discord_channels'],
        'grab_past_flag': 1
    }
    # save_setup(setup_data)
    # flash('Settings updated successfully!')
    # return redirect(url_for('advanced_setup'))
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
        print("User not logged in")
        return redirect(url_for('index'))

    sp = spotipy.Spotify(auth=token_info['access_token'])

    first_playlist = playlist_array[0]
    fline = first_playlist[1].replace("https://open.spotify.com/playlist/", "")
    PLAYLISTID = (fline.split("?si")[0])

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

    open('uri.txt', 'w+').close()

    spotifyRQ1 += " SUCCESS Spotify has been linked!"
    return render_template('index.html', num_songs=spotifyRQ1, timestamp=timestamp)

@app.route('/close_app', methods=['POST'])
def close_app():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/continue_setup', methods=['POST'])
def continue_setup():
    return render_template('advanced_setup.html')

@app.route('/advanced_setup', methods=['GET', 'POST'])
def advanced_setup():
    if request.method == 'POST':
        # Add logic to handle advanced setup form inputs if needed
        flash('Setup updated!')
        return redirect(url_for('advanced_setup'))

    return render_template('advanced_setup.html')

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
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope='playlist-modify-public user-library-read'
    )
