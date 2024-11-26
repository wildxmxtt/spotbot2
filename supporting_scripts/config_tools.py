from datetime import datetime
import json
import time, os

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
    print(message + "signature: " + pgrm_signature)

    now = time_now()

    try:
        with open(log_file, 'a') as f:
            f.write(now + ' - ' + message + " python file: " + pgrm_signature)
            f.write('\n')
    except FileNotFoundError as e:
        print("Please make sure file exists in logs/<your_file_name.log>"+ str(e))
        time.sleep(60)



def file_name(file_name = __file__):
    return(os.path.basename(file_name))