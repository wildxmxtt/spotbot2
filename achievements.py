import sqlite3
import time
from playlist_update import get_playlist_duration

pgrm_signature = "achievements.py: "

# Checks the Duration acheievements and returns the string of the message that celebrates users
def checkDurationAchievement(length):
    # connect to database
    conn = sqlite3.connect('databases/spotbot.db')
    cur = conn.cursor()

    try:
        cur.execute('''SELECT milestone FROM playlist_duration_milestones
            WHERE milestone = ? AND reached_at IS NULL''',
            (int(length),))
        milestone = cur.fetchone()
        
        if milestone:
            cur.execute('''UPDATE playlist_duration_milestones
                        SET reached_at = ?
                        WHERE milestone = ?
                        ''',
                        (time.time(), int(length)))
            conn.commit()

            return f"Wow! The playlist has reached {milestone[0]} hours in lenght!"
        else:
            return False
        
    except ValueError:
        print(f"Error: '{length}' must be a valid number")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    # close the connection
    conn.close()

# Recieves the number of total songs in the playlist and sends acheivement messages (if enabled via Flask)
def checkAchievement(numberOfMessages, grab_past_flag):
    # Acheivements go 25, 50, 69, 100, 200, etc

    # Do not print out on a grab past
    if (grab_past_flag == 1):
        # Small number acheivements
        if numberOfMessages < 100:
            if (numberOfMessages % 25 == 0) and (numberOfMessages != 75):
                # print the number and a success
                return f"The playlist has reached {numberOfMessages} songs!"

            elif numberOfMessages == 69:
                # print out the haha funny
                return f"The playlist has reached {numberOfMessages} songs! Nice!"

        elif numberOfMessages % 100 == 0:
            # print out he number of songs
            return f"Woah! The playlist has reached {numberOfMessages} songs!"
    
    # if grab past has not been called on start up or no acheivment has been metreturn false
    return False