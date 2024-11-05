from datetime import datetime
import json
import time, os

def config_data():
    with open("setup.json", 'r') as setupf:
        data = json.load(setupf)
        TOKEN = (data['discord_token'])
        client_id = (data['client_id'])
        client_secret = (data['client_secret'])
        playlist_channel = (data['playlist_channel'])
        # playlist_link = (data['playlist_link'])
        grab_past_flag = (data['grab_past_flag'])
        use_init_spotify_token = (data['use_init_spotify_token'])
        check_past_on_boot = (data['check_past_on_boot'])
        # discord_channel = (data['discord_channels'])

    pc = playlist_w_channel_setup(playlist_channel)

    #data dict to use throughout program
    data_dict = {
        'discord_token': TOKEN,
        'client_id': client_id,
        'client_secret': client_secret,
        'grab_past_flag': grab_past_flag,
        'pc': pc, 
        'init_spotify_flag': use_init_spotify_token,
        'check_past_on_boot': check_past_on_boot
    }

    return data_dict


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
    print(message + "signature: " + pgrm_signature)

    now = time_now()

    try:
        with open(log_file, 'a') as f:
            f.write(now + ' - ' + message + " python file: " + pgrm_signature)
            f.write('\n')
    except Exception as e:
        print("Please make sure file exists in logs/<your_file_name.log>"+ e)
        time.sleep(60)



def file_name(file_name = __file__):
    return(os.path.basename(file_name))