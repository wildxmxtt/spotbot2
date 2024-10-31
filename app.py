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
SECRET_DATABASE = 'setup.json'
# Sets up our secret information into the application from secrets.db
secret_setup_info = dbt.get_setup_info(SECRET_DATABASE)
client_id = secret_setup_info['client_id']
client_secret = secret_setup_info['client_secret']
TOKEN = secret_setup_info['discord_token']

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
        clear_table_input = request.form.get('clear_table_input')
        if clear_table_input == 'DELETE':
            # Get the selected table from the form data
            selected_table = request.form.get('table')

            if selected_table:
                # Clear the table
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM {}".format(selected_table))
                conn.commit()
                conn.close()

                # Redirect to the same page to refresh the table
                return redirect(url_for('view_database', db_name=db_name))
            else:
                # Handle the case where no table is selected
                flash("Please select a table to delete from.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]

    table_data = None
    column_names = None
    selected_table = None

    if request.form.get('table'):
        selected_table = request.form.get('table')

        cursor.execute("SELECT * FROM {}".format(selected_table))
        column_names = [description[0] for description in cursor.description]
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


@app.route('/edit_chats', methods=['POST'])
def edit_chats():
    conn = sqlite3.connect(SECRET_DATABASE)
    cursor = conn.cursor()

    chats_data = request.form.getlist('chats_data')  # Get all the inputs from the form
    num_fields = 3  # Number of fields per row: id, playlist_link, discord_channel
    chat_entries = [chats_data[i:i + num_fields] for i in range(0, len(chats_data), num_fields)]

    for entry in chat_entries:
        chat_id, playlist_link, discord_channel = entry
        
        # Check if it's an existing row or a new row (new rows will have an empty chat_id)
        if chat_id:
            cursor.execute('''UPDATE chats
                              SET playlist_link = ?, discord_channel = ?
                              WHERE chat_id = ?''', (playlist_link, discord_channel, chat_id))
        else:
            # Insert new row
            cursor.execute('''INSERT INTO chats (playlist_link, discord_channel)
                              VALUES (?, ?)''', (playlist_link, discord_channel))

    conn.commit()
    conn.close()
    
    flash("Chats configuration updated successfully!")
    return redirect(url_for('advanced_setup'))

@app.route('/update_chats', methods=['POST'])
def update_chats():
    conn = sqlite3.connect(SECRET_DATABASE)
    cursor = conn.cursor()

    # Retrieve all column names from the chats table
    cursor.execute("PRAGMA table_info(chats)")
    column_info = cursor.fetchall()
    column_names = [info[1] for info in column_info]  # Extract column names
    
    # Retrieve all rows from the chats table
    cursor.execute("SELECT * FROM chats")
    chats = cursor.fetchall()

    # Loop through each row in the table
    for row_index, row in enumerate(chats):
        # Check if the user has typed DELETE for the row
        delete_value = request.form.get(f"delete_row_{row_index}")
        if delete_value == "DELETE":
            # Delete the row if DELETE is typed
            cursor.execute("DELETE FROM chats WHERE chat_id = ?", (row[0],))  # Assuming chat_id is in the first column
            continue
        
        # Prepare to update the row with new values from the form
        updated_values = []
        for column_index, column_name in enumerate(column_names):
            # Skip the first column (assuming it's the chat_id and should not be updated)
            if column_name == "chat_id":
                continue
            updated_value = request.form.get(f"row_{row_index}_{column_index}")
            updated_values.append(updated_value)
        
        # Dynamically create the SQL update query using the column names
        set_clause = ", ".join([f"{column} = ?" for column in column_names[1:]])  # Skip 'chat_id'
        cursor.execute(f"""
            UPDATE chats
            SET {set_clause}
            WHERE chat_id = ?
        """, (*updated_values, row[0]))  # Assuming 'chat_id' is in the first column

    conn.commit()
    conn.close()
    
    flash("Chats updated successfully!")
    return redirect(url_for('advanced_setup'))



@app.route('/add_chat_row', methods=['GET', 'POST'])
def add_chat_row():
    conn = sqlite3.connect(SECRET_DATABASE)
    cursor = conn.cursor()
    
    # Insert a new row with default values (e.g., empty strings or appropriate defaults)
    cursor.execute("INSERT INTO chats (playlist_link, discord_channel) VALUES (?, ?)", ("", ""))
    conn.commit()
    conn.close()

    flash("New row added successfully!")
    return redirect(url_for('advanced_setup'))

@app.route('/advanced_setup', methods=['GET', 'POST'])
def advanced_setup():
    secret_setup_info = dbt.get_secret_setup_info_dict(SECRET_DATABASE)
    client_id = secret_setup_info['client_id']
    client_secret = secret_setup_info['client_secret']
    
    chats_info =dbt.update_spotbot_chat(SECRET_DATABASE)

    return render_template(
        'advanced_setup.html', 
        client_id=client_id, 
        client_secret=client_secret, 
        discord_token=chats_info[0]['discord_token'],
        playlist_links=chats_info[1]['playlist_links'], 
        discord_channels=chats_info[0]['discord_channels'], 
        installed_features=installed_features,
        chats=chats_info[3],  # Pass chats data to template
        column_names=chats_info[2]  # Pass column names to template
    )

@app.route('/save_setup', methods=['POST'])
def save_setup():
    # Your logic to save setup information
    # Example:
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    discord_token = request.form.get('discord_token')
    playlist_links = request.form.get('grab_past_flag')
    discord_channels = request.form.get('discord_channels')
    
    # Save these details to the database, probably using the functions in database_tools.py
    dbt.save_secrets_to_db(client_id, client_secret, discord_token, playlist_links, discord_channels)
    
    flash("Secret Setup saved successfully!")
    return redirect(url_for('advanced_setup'))  # Redirect back to advanced_setup or another page


@app.route('/save_advanced_setup', methods=['POST'])
def save_advanced_setup():
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    discord_token = request.form.get('discord_token')
    
    # Save these details to the database, probably using the functions in database_tools.py
    dbt.save_secrets_to_db(client_id, client_secret, discord_token, tokensOnlyFlag=True)

    flash('Settings updated successfully!')
    return redirect(url_for('advanced_setup'))

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
    file = '.cache'
    if(os.path.exists(file)):
        #os.remove(file)
        print("WARNING: cache file found, this can cause token login issues, please delete & use private/incoginto browser IF possible, you are expirencing SPOTIFY LOGIN issues!")
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect(url_for('index'))
    
    playlist_link = dbt.get_playlist_link(SECRET_DATABASE) 
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

    open('uri.txt', 'w+').close()

    spotifyRQ1 += " SUCCESS Spotify has been linked!"
    return render_template('index.html', num_songs=spotifyRQ1, timestamp=timestamp, playlist_name = playlist_link )

@app.route('/close_app', methods=['POST'])
def close_app():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/continue_setup', methods=['POST'])
def continue_setup():
    chats_info =dbt.update_spotbot_chat(SECRET_DATABASE)

    return render_template(
        'setup.html', 
        client_id=client_id, 
        client_secret=client_secret, 
        discord_token=chats_info[0]['discord_token'],
        playlist_links=chats_info[1]['playlist_links'], 
        discord_channels=chats_info[0]['discord_channels'], 
        installed_features=installed_features,
        chats=chats_info[3],  # Pass chats data to template
        column_names=chats_info[2]  # Pass column names to template
    )

    return render_template('setup.html', installed_features=installed_features)

# @app.route('/advanced_setup', methods=['GET', 'POST'])
# def advanced_setup():
#     if request.method == 'POST':
#         # Add logic to handle advanced setup form inputs if needed
#         flash('Setup updated!')
#         return redirect(url_for('advanced_setup'))

#     return render_template('advanced_setup.html')

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
    secret_setup_info = dbt.get_setup_info(SECRET_DATABASE)
    if secret_setup_info is not None:
        client_id = secret_setup_info['client_id']
        client_secret = secret_setup_info['client_secret']
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope='playlist-modify-public user-library-read'
    )

if __name__ == '__main__':
    app.run(debug=True)