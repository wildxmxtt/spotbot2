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
        'discord_token': 2            
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


def save_secrets_to_db(client_id, client_secret, discord_token, playlist_links = 'None_Given', discord_channels = 'None_Given', SECRET_DATABASE=r'databases\secrets.db', tokensOnlyFlag=False):
    conn = sqlite3.connect(SECRET_DATABASE)
    cur = conn.cursor()
    ##TO-DO## 
    #Add a check to see if there is a record in the table, if not add one. Else always update, give feedback to user that previous record was over written.
    #Possbily add future to run multiple spotbots??? Not sure if we even would need that though. Need to talk with Karl about this.


    # Insert or update the setup information in the database
    cur.execute("""
        INSERT OR REPLACE INTO setup (client_id, client_secret, discord_token) 
        VALUES (?, ?, ?)
    """, (client_id, client_secret, discord_token))
    
    conn.commit()

    if(tokensOnlyFlag == False or playlist_links != 'None_Given' or discord_channels != 'None_Given'):
    #need to iterate through playlist_links and discord_channels make a robust system to accosicate discord channel to playlist link
        cur.execute("""
            INSERT OR REPLACE INTO chats (playlist_link, discord_channel) 
            VALUES (?, ?)
        """, (playlist_links, discord_channels))

        conn.commit()
    conn.close()
    print("Added chats config toi db")

def save_spotbot_chats_config_to_db(playlist_links, discord_channels,SECRET_DATABASE=r'databases\secrets.db'):
    conn = sqlite3.connect(SECRET_DATABASE)
    cur = conn.cursor()
    
    # Insert or update the setup information in the database
    cur.execute("""
        INSERT OR REPLACE INTO setup (client_id, client_secret, discord_token, grab_past_flag) 
        VALUES (?, ?, ?, ?, ?)
    """, (playlist_links, discord_channels))
    
    conn.commit()
    conn.close()
    print("Added chats config toi db")

def retrieve_secrets_info(SECRET_DATABASE=r'databases\secrets.db'):
    conn = sqlite3.connect(SECRET_DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT client_id, client_secret, discord_token, grab_past_flag FROM setup WHERE 1 = 1")
    secrets_info = cur.fetchone()
    conn.close()
    return secrets_info

def get_spotbot_chats_config_info(SECRET_DATABASE=r'databases\secrets.db'):
    conn = sqlite3.connect(SECRET_DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT playlist_link, discord_channel FROM chats WHERE 1 = 1")
    chats_info = cur.fetchone()
    conn.close()
    return chats_info
# secret_setup_info = get_secret_setup_info_dict('spotbot.db')
# secret_setup_info = get_setup_info(r'databases\secrets.db')


# secret_setup_info = get_secret_setup_info_dict(r'databases\secrets.db')
# client_id = secret_setup_info['client_id']
# client_secret = secret_setup_info['client_secret']

# get_secret_setup_info_dict(r'databases\secrets.db')

def update_spotbot_chat(SECRET_DATABASE):
    secrets_info_dict = {
        'client_id': "",
        'client_secret': "",
        'discord_token': "",
        'playlist_links': "",
        'discord_channels': ""
    }
    
    chats_info_dict = {
        'playlist_links' : "",
        'discord_channels' : "",
        'chats_info' : ""
    }

    conn = sqlite3.connect(SECRET_DATABASE)
    cursor = conn.cursor()
    
    # Fetch chats table data
    cursor.execute("SELECT * FROM chats")
    chats = cursor.fetchall()

    # Fetch column names for rendering table headers
    cursor.execute("PRAGMA table_info(chats)")
    column_names = [info[1] for info in cursor.fetchall()]  # Extract column names
    
    conn.close()

    secrets_info = retrieve_secrets_info(SECRET_DATABASE)
    chats_info = get_spotbot_chats_config_info(SECRET_DATABASE)

    secrets_info = secrets_info or ('', '', '', '')
    chats_info = chats_info or ('', '')
    
    client_id, client_secret, discord_token, grab_past_flag = secrets_info
    playlist_links, discord_channels = chats_info
    
    secrets_info_dict.update({'client_id' : client_id, 'client_secret': client_secret, 'discord_token': discord_token, 'playlist_links': playlist_links, 'discord_channels': discord_channels})
    chats_info_dict.update({'playlist_links': playlist_links, 'discord_channels': discord_channels})

    client_id, client_secret, discord_token, grab_past_flag = secrets_info
    playlist_links, discord_channels = chats_info

    return secrets_info_dict, chats_info_dict, column_names, chats