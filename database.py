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
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

# Print the table names
if tables:
    print("Tables in the database:")
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")

        # Get the column names for the current table
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = cur.fetchall()

        # Print the column names
        print("Columns:")
        for column in columns:
            column_name = column[1]
            print(f"- {column_name}")
else:
    print("No tables found in the database.")

conn.close()