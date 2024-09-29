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
def get_setup_info(file):
    # Connect to database
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    # Get server setup info for the server
    cur.execute("SELECT * FROM setup")

    sql_results = cur.fetchone()
    conn.close()

    # Return information
    return sql_results

def get_secret_setup_info_dict(file):

    setup_info_dict = {
        'client_id': 0,
        'client_secret': 1,
        'discord_token': 2,
        'grab_past_flag': 3,
        'leaderboards_flag': 4,
        'server_name': 5                
    }

    # Connect to database
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    # Get server setup info for the server
    cur.execute("SELECT * FROM setup")

    sql_results = cur.fetchone()
    conn.close()
    if sql_results is not None:
        for i in range(len(setup_info_dict)):
            setup_info_dict[list(setup_info_dict.keys())[i]] = list(sql_results)[i]

        # Return information
        return setup_info_dict
    else: 
        return None


def get_pub_setup_info_dict(file):

    setup_info_dict = {
        'client_id': 0,
        'client_secret': 1,
        'discord_token': 2,
        'grab_past_flag': 3,
        'leaderboards_flag': 4,
        'server_name': 5                
    }

    # Connect to database
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    # Get server setup info for the server
    cur.execute("SELECT * FROM songs")

    sql_results = cur.fetchone()
    conn.close()

    for i in range(len(setup_info_dict)):
        setup_info_dict[list(setup_info_dict.keys())[i]] = list(sql_results)[i]

    # Return information
    return setup_info_dict


# Returns tuples of playlist information. Index 0 is the playlist link, index 1 is the discord channel ID
def get_playlist_array(file):
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    cur.execute("SELECT playlist_link,discord_channel FROM chats")

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

# secret_setup_info = get_secret_setup_info_dict('spotbot.db')
# secret_setup_info = get_setup_info(r'databases\secrets.db')


# secret_setup_info = get_secret_setup_info_dict(r'databases\secrets.db')
# client_id = secret_setup_info['client_id']
# client_secret = secret_setup_info['client_secret']