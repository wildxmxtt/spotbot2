import sqlite3

def main():
    # Setup info    
    setup = input("Alter setup info? (y/n)").lower()
    if setup == 'y':
        print("Overwriting setup information if any exists...")
        
        conn = sqlite3.connect("secrets.db")
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM setup")
        
        client_id = input("Input the client ID")
        client_secret = input("Input the client secret")
        discord_token = input("Input the discord token")
        leaderboards = input("Enable leaderboards? (y/n)").lower()

        if leaderboards == 'y':
            leaderboards_flag = 1
        else:   leaderboards_flag = 0
        
        cursor.execute('''
        INSERT INTO setup (client_id, client_secret, discord_token, grab_past_flag, leaderboards_flag)
        VALUES (?, ?, ?, 0, ?)
        ''', (client_id, client_secret, discord_token, leaderboards_flag)) # Grab past flag is automatically set to 0
        
        conn.commit()
        conn.close()
        
        print("Setup table populated")
    else:
        print("No changes made to the setup table")

    # Playlist info
    conn = sqlite3.connect("secrets.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM chats")
    results = cursor.fetchall()

    if results:
        print("Current information in chats:\n")
        for result in results:
            print(result)
        answer = input("\nDo you want to re-input infromation with starter playlist?(y/n) ").lower()
        if answer == 'y': cursor.execute("DELET FROM chats")

    if not results or answer == 'y':
        playlist_link = input("Input the playlist link: ")
        channel = input("What discord channel should be linked to this playlist: ")

        cursor.execute('''
        INSERT INTO chats (playlist_link, discord_channel)
        VALUES (?,?)
        ''', (playlist_link, channel))

        conn.commit()
        conn.close()

        print("Chats table populated")
    else:
        print("No changes made to the chats table") 


if __name__ == "__main__":
    main()