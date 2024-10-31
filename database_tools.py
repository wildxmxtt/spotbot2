from os import path
import json
import sqlite3

pgrm_signature = "database_tools.py"


def initialize_milestones(file, playlist_array):
    # Check to see if the database file already exists
    if not path.exists(file):
        print(f'ERROR {pgrm_signature}: {file} does not exist!')
    
    # If the database exists connect and playlist_duration tables
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    for playlist in playlist_array:
        playlist_ID = playlist['playlist'].split('/')[-1].split('?')[0] # Extract playlist ID

        # If the playlist ID is in the database return false
        cur.execute('SELECT playlist_id from playlist_duration_milestones WHERE playlist_id = ?', (playlist_ID, ))
        entries = cur.fetchone()

        if entries:
            conn.close()
            return True
        else:
            # If the playlist ID is not in the database create milestones
            milestones = [1, 5, 10, 25, 30, 40, 50, 75, 100, 125, 150, 200, 500]
            for milestone in milestones:
                cur.execute('INSERT INTO playlist_duration_milestones(playlist_id,milestone) VALUES(?,?)', (playlist_ID, milestone, ))

            # Return true and report actions
            print(f"{pgrm_signature}: Duration database updated for {playlist}")
            conn.commit()
            conn.close()
            return True

# Returns setup information. Indexes are as follows:
# 0 client id, 1 client secret, 2 discord token, 3 grab past flag, 4 leaderboards flag, 5 server name
def get_setup_info(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    # Return information
    return data

# Returns tuples of playlist information. Index 0 is the playlist link, index 1 is the discord channel ID
def get_playlist_array(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    return data["playlist_channel"]
    
# Returns the playlist link using the chat ID
def get_playlist_link(file_name, chat_ID=None):
    with open(file_name, 'r') as file:
        data = json.load(file)

    # Extract playlist info from JSON
    playlist_channel = data["playlist_channel"]

    if chat_ID is None:
        # flask get tracks test
        first_playlist = playlist_channel[0]["playlist"]

        # Return the first playlist link available
        return first_playlist
    
    else:
        # Regular use: return playlist link defined by chat ID from JSON
        for playlist in playlist_channel:
            if chat_ID in playlist["channel"]:
                return playlist["playlist"]
