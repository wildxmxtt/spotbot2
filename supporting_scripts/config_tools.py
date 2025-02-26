from datetime import datetime
import json
import time, os
import re

def config_data(file='setup.json'):
    with open(file, 'r') as setupf:
        data = json.load(setupf)

    setupf.close()
    return data
#function to setup channel playlist relationships from json here
def playlist_w_channel_setup(playlist_channel):
    pc_relationship = {}
    i = 0
    #writes items from json to dict
    for item in playlist_channel:
        pc_relationship[i] = {
            'playlist': item['playlist'],
            'channel': item['channel']
        }
        i += 1
    #returns dict
    return pc_relationship

def time_now():
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    return current_time

def logs(message, log_file = r'logs/default.log', pgrm_signature = __file__):
    pgrm_signature = file_name(pgrm_signature)

    now = time_now()

    try:
        with open(log_file, 'a') as f:
            f.write(now + ' - ' + message + " python file: " + pgrm_signature)
            f.write('\n')
    except FileNotFoundError as e:
        print("Please make sure file exists in logs/<your_file_name.log>: "+ str(type(e).__name__))

# Returns the Spotify track or playlist ID from various URL types
def getSpotifyID(url):
    # Regex patterns for regular, uri, and shortened spotify links. AI code.
    patterns = [
        r'https://open\.spotify\.com/(track|playlist)/([a-zA-Z0-9]+)',
        r'spotify:(track|playlist):([a-zA-Z0-9]+)',
        r'spotify\.link/([a-zA-Z0-9]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match: # If spotify ID found return
            return match.group(2)
            

    # If no spotify ID found return None
    return None


def validate_spotify_uris(uri_list, min_length=20, max_length=25):
    # Regular expression for Spotify URIs: alphanumeric strings within a length range
    pattern = re.compile(rf'^[A-Za-z0-9]{{{min_length},{max_length}}}$')
    
    # Validate each URI in the list
    results = [bool(pattern.match(uri)) for uri in uri_list]
    
    return results

def file_name(file_name = __file__):
    return(os.path.basename(file_name))

def split_large_list(input_list, chunk_size=50):
    """
    Splits a list into smaller lists with a maximum size of `chunk_size`.
    
    Args:
        input_list (list): The list to be split.
        chunk_size (int): Maximum number of items in each chunk (default is 50).
    
    Returns:
        list of lists: A list containing the smaller chunks.
    """
    # Split the input list into chunks of size `chunk_size`
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]