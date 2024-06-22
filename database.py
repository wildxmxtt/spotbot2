# A file for manipulating the database in development

import sqlite3

# Connect to or create SQLite Database
conn = sqlite3.connect('spotbot.db') # create or connect to the database

# Create a cursor
cur = conn.cursor()

# Create the "songs" table
# cur.execute('''CREATE TABLE IF NOT EXISTS songs
#              (song_table_ID INTEGER PRIMARY KEY, spotify_ID TEXT, sender_ID INTEGER, FOREIGN KEY (sender_ID) REFERENCES senders(sender_ID))''')

# Create the "senders" table
# cur.execute('''CREATE TABLE IF NOT EXISTS senders
#              (sender_ID INTEGER PRIMARY KEY, username TEXT)''')

# Get a list of tables in the database
# cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cur.fetchall()

# Get all of the spotify IDs in the db
cur.execute("SELECT spotify_ID FROM songs")
songs = cur.fetchall()
for song in songs:
    print(song)

conn.close()