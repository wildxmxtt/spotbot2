from os import path
import json
import sqlite3

pgrm_signature = "database_tools.py"

playlist_array = []

with open("setup.json", 'r') as setupf:
    data = json.load(setupf)
    TOKEN = (data['discord_token'])
    client_id = (data['client_id'])
    client_secret = (data['client_secret'])
    playlists = (data['playlists'])
    grab_past_flag = (data['grab_past_flag'])
    leaderboards_flag = (data['leaderboards_flag'])

    for playlist in playlists:
        # Extract playlist attributes
        playlist_name = playlist['playlist_name']
        playlist_link = playlist['playlist_link']
        discord_channel = playlist['discord_channel']
        
        # Add to playlist array
        playlist_array.append([playlist_name, playlist_link, discord_channel])

def initialize_database(file):
    # Check to see if the database file already exists
    db_exists = path.exists(file)

    # If the databse doesn't exist, create the tables
    if not db_exists:
        tables = [
            f"""
            CREATE TABLE IF NOT EXISTS songs (
            song_table_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            spotify_ID TEXT,
            playlist_ID TEXT,
            sender_ID INTEGER,
            timestamp TEXT,
            discord_message_id TEXT
            )
            """,
            f"""
            CREATE TABLE IF NOT EXISTS playlist_duration_milestones (
            playlist_id TEXT,
            milestone INTEGER,
            reached_at DATETIME,
            PRIMARY KEY (playlist_id, milestone)
            )
            """]

        conn = sqlite3.connect(file)
        cur = conn.cursor()

        # Execute the statements
        cur.execute(tables[0])
        cur.execute(tables[1])

        print(f"{pgrm_signature}: Fresh database initialized.")

        # Commit the changes
        conn.commit()
        conn.close()

        # Break from the function if fresh tables are created
        return True
    
    # If the database exists connect and playlist_duration tables
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    for playlist in playlist_array:
        playlist_ID = playlist[1].split('/')[-1].split('?')[0] # Extract playlit ID

        # If the playlist ID is in the database return false
        entries = cur.execute('SELECT playlist_id from playlist_duration_milestones WHERE playlist_id = ?', (playlist_ID, ))
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