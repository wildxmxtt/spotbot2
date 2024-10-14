import sqlite3
import getpass


def get_input(prompt, is_secret=False):
    if is_secret:
        return getpass.getpass(prompt + ": ")
    else:
        return input(prompt + ": ")

def main():
    setup = get_input("Alter setup info? (y/n)").lower()
    if setup == 'y':
        print("Overwriting setup information if any exists...")
        
        conn = sqlite3.connect("secrets.db")
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM setup")
        
        client_id = get_input("Input the client ID", is_secret=True)
        client_secret = get_input("Input the client secret", is_secret=True)
        discord_token = get_input("Input the discord token", is_secret=True)
        leaderboards = get_input("Enable leaderboards? (y/n)").lower()

        if leaderboards == 'y':
            leaderboards_flag = 1
        else:   leaderboards_flag = 0
        
        cursor.execute('''
        INSERT INTO setup (client_id, client_secret, discord_token, grab_past_flag, leaderboards_flag)
        VALUES (?, ?, ?, 0, ?)
        ''', (client_id, client_secret, discord_token, leaderboards_flag)) # Grab past flag is automatically set to 0
        
        conn.commit()
        conn.close()
        
        print("Database populated.")
    else:
        print("No changes made to the database.")
    

if __name__ == "__main__":
    main()