#!/bin/bash
read -p 'alter setup info?(y/n)' setup
if [$setup == y]; then
echo Overwritting set-up information if any exists...

sqlite3 "secrets.db" "DELETE FROM setup"

read -sp 'Input the client ID: ' client_id

read -sp 'Input the client secret: ' client_secret

read -sp 'Input the discord token: ' discord_token

while
    read -p 'Enable leaderboards? (y/n) ' leaderboards
    [[$leaderboards == y || $leaderboards == n]]
do true; done
sqlite3 "secrets.db" "INSERT INTO setup (client_id, client_secret, discord_token, grab_past_flag, leaderboards_flag) VALUES ('$client_id', '$client_secret', '$discord_token', 0, $leaderboardsflag)"

echo Database populated.
fi

