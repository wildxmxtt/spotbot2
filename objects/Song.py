import re
import sqlite3
from pathlib import Path

class Song:
    ''' A song from Spotify'''
    def __init__(self, song):
        self.song = song

    def getSong(self):
        ''' Returns the song feild'''
        return self.song

    def getSpotifyID(self, content):
        ''' Returns the Spotify track ID from various URL types'''
        # Regex patterns for regular, uri, and shortened spotify links. AI code.
        patterns = [
            r'https://open\.spotify\.com/(track|playlist)/([a-zA-Z0-9]+)',
            r'spotify:(track|playlist):([a-zA-Z0-9]+)',
            r'spotify\.link/([a-zA-Z0-9]+)',
            r'([a-zA-Z0-p]+)'
        ]

        # Itterate through all patters
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                if len(match.groups()) == 2:    # if both the content type and spotify id are persent
                    content_type, spotify_id = match.groups()
                    if content_type == 'playlist':  # Return none if playlist
                        return None
                
                # Extract the spotifyID and return it
                spotify_id = match.group(1)
                return spotify_id

        # Return none if no spotifyID is found
        return None
    
    def checkDatabase(self, playlistID):
        ''' Checks if the song is in the database'''
        songID = self.song

        # Connect to a database
        db_path = Path(__file__).resolve().parent.parent / 'databases' / 'spotbot.db'
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Attempt to select the Spotify ID, must also be in the specified playlist
        cur.execute("SELECT spotify_ID FROM songs WHERE spotify_ID = ? AND playlist_ID = ? LIMIT 1", (songID,playlistID,))
        matches = cur.fetchone()

        # If the song is found return True
        if matches:
            return True
        
        # If the song is not found return False
        return False
    
    def addSongToDatabase(self, playlistID, sender, time, messageID):
        ''' Adds song to the database while recording the sender, time, and Discord message ID'''
        
        # Connect to a database
        db_path = Path(__file__).resolve().parent.parent / 'databases' / 'spotbot.db'
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        print(f'Adding {self.song} to database')
        cur.execute("INSERT INTO songs (spotify_ID, playlist_ID, sender_ID, timestamp, discord_message_id) VALUES (?, ?, ?, ?, ?)", 
                (self.song, playlistID, sender, time, messageID))
        conn.commit()
            
        conn.close()
        return True