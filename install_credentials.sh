#!/bin/bash


# Function to get user input
get_input() {
    local prompt="$1"
    local var_name="$2"
    local is_secret="$3"

    if [ "$is_secret" = "true" ]; then
        read -sp "$prompt: " "$var_name"
        echo
    else
        read -p "$prompt: " "$var_name"
    fi
}

get_input "alter setup info?(y/n): " setup
if [ "$setup" = "y" ]; then
    echo Overwritting set-up information if any exists...

    sqlite3 "secrets.db" "DELETE FROM setup"

    get_input "Input the client ID" client_id true

    get_input "Input the client secret" client_secret true

    get_input "Input the discord token" discord_token true

    get_input "Enable leaderboards? (y/n)" leaderboards
    if [[ "$leaderboards" == "y" ]]; then
        leaderboards_flag="1"
    else
        leaderboards_flag="0"
    fi

sqlite3 "secrets.db" "INSERT INTO setup (client_id, client_secret, discord_token, grab_past_flag, leaderboards_flag) VALUES ('$client_id', '$client_secret', '$discord_token', 0, $leaderboards_flag)"

echo Database populated.
fi

