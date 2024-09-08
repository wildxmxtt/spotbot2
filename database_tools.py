from os import path
import json
import sqlite3

pgrm_signature = "database_tools.py"


def initialize_database(file, playlist_array):
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
def get_setup_info(file, server_name):
    # Connect to database
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    # Get server setup info for the server
    cur.execute("SELECT * FROM setup WHERE server_name = ?", (server_name,))

    sql_results = cur.fetchone()
    conn.close()

    # Return information
    return sql_results

# Returns tuples of playlist information. Index 0 is the playlist link, index 1 is the discord channel ID
def get_playlist_array(file, server_name):
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    cur.execute("SELECT playlist_link,discord_channel FROM chats WHERE server_name = ?", (server_name,))

    sql_results = cur.fetchall()
    conn.close()

    return sql_results

# Returns the playlist link using the chat ID
def get_playlist_link(file, chat_ID):
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    # query for the playlist ID
    cur.execute("SELECT playlist_link FROM chats WHERE discord_channel = ?", (chat_ID,))

    playlist_link = cur.fetchone()
    conn.close()

    return playlist_link

