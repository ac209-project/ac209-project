# Imports
import numpy as np
import pandas as pd
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Set up oath
client_credentials_manager = SpotifyClientCredentials(client_id = '99fd6b637f19418996f726efd4f57aa3',
                                                      client_secret='00331cf90a064cafa7223fd9b6c6b8c5')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Get Users
with open('offset_0_1050.txt','r') as file:
    users = file.read().split('\n')[:-1]

# Get user followers for each user

def get_users_followers():
    """ NOTE: THIS WILL TAKE 4.5-5.5  HOURS TO RUN!!!!
    Also, users is a global variable..."""
    user_dict = {'user': [], 'user_followers': []}
    # for chunk in range(0,8470,10):
    #     time.sleep(2)
    #     t0 = time.time()
    for i,user in enumerate(users):
        time.sleep(2)
        t0 = time.time()
        try:
            u = sp.user(user)
        except:
            continue
        try:
            user_dict['user'].append(user)
            user_dict['user_followers'].append(u['followers']['total'])
        except:
            continue
        print('that took {0} sec for num {1}'.format(time.time()-t0,i))

    udf = pd.DataFrame(user_dict)
    try:
        udf.to_json('user_follow.json')
    except:
        udf.index = pd.RangeIndex(len(udf.index))
        udf.to_json('user_follow.json')

# Running commands
get_users_followers()

# Aggregate mini-dataframes into larger dataframes
# plists = pd.read_json('dfs/plist_part0.json')
# tracks = pd.read_json('dfs/track_part0.json')
#
# for chunk in range(10,8470,10):
#     temp_track = pd.read_json('dfs/track_part{}.json'.format(chunk))
#     temp_plist = pd.read_json('dfs/plist_part{}.json'.format(chunk))
#     plists = plists.append(temp_plist)
#     tracks = tracks.append(temp_track)
#
# # Reset Index
# plists.index = pd.RangeIndex(len(plists.index))
# tracks.index = pd.RangeIndex(len(tracks.index))

# Save JSON dataframes
# plists.to_json('data/plist_df.json')
# tracks.to_json('data/track_df.json')
