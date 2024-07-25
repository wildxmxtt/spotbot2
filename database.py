# Table: songs
# ------------
# song_table_ID: INTEGER  
# spotify_ID: TEXT        
# sender_ID: INTEGER      
# timestamp: TEXT
# discord_message_id: TEXT

# A file for manipulating the database in development

import sqlite3
from datetime import datetime
import calendar

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



cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

# For each table, get and print column information
for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")
    print("-" * (len(table_name) + 7))
    
    # Get column information
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = cur.fetchall()
    
    # Print column names and types
    for column in columns:
        col_name = column[1]
        col_type = column[2]
        print(f"{col_name}: {col_type}")

# cur.execute("SELECT * FROM songs")
# table = cur.fetchall()

# for entry in table:
#     print(entry)

# # Execute the SELECT statement
# cur.execute("""
#     SELECT sender_ID, COUNT(*) as song_count
#     FROM songs
#     GROUP BY sender_ID
#     ORDER BY song_count DESC
# """)

# # Fetch all results
# results = cur.fetchall()

# Print the results
# print("Sender ID | Number of Songs")
# print("--------------------------")
# for row in results:
#     sender_id, song_count = row
#     print(f"{sender_id:9d} | {song_count:16d}")

# # Close the connection
# conn.close()

# print("Deleting all songs now\n")

# cur.execute("DELETE FROM songs")
# conn.commit()

# Print out massagesIDs from last month
# Get the current year and month
# current_date = datetime.now()
# current_year = current_date.year
# current_month = current_date.month

# # Get top 10 users and their number of songs added for the current month
# cur.execute("""
#     SELECT discord_message_id, timestamp, spotify_id
#     FROM songs
#     WHERE strftime('%Y', timestamp) = ? AND strftime('%m', timestamp) = ?
#     LIMIT 10
# """, (str(current_year), f"{current_month:02d}"))

# ids = cur.fetchall()

# for id in ids:
#     print (id)

conn.close()
