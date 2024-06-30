# +----------------------+
# |        songs         |
# +----------------------+
# | id (INTEGER PRIMARY) |
# | content (TEXT)       |
# | timestamp (TEXT)     |
# | discord_message_id   |
# |        (TEXT)        |
# +----------------------+

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



# print(f"songs:\n\n{table}")

cur.execute("SELECT * FROM songs")
table = cur.fetchall()

for entry in table:
    print(entry)

# Execute the SELECT statement
# cur.execute("""
#     SELECT sender_ID, COUNT(*) as song_count
#     FROM songs
#     GROUP BY sender_ID
#     ORDER BY song_count DESC
# """)

# # Fetch all results
# results = cur.fetchall()

# # Print the results
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


conn.close()