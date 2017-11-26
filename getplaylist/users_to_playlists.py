# Imports
import numpy as np
import pandas as pd
import time

# Get Users
with open('getplaylist/offset_0_1050.txt','r') as file:
    users = file.read().split('\n')[:-1]

# Get playlist and track data for each user
# THIS TAKES AROUND 8-9 HOURS!!!!!!!!!
"""
NOTE: General info about columns below:
collaborative returns t/f
description returns text
take nothing from external_urls
followers['total'] is the int
nothing from href
id is the id
nothing from image
text from name
can get username from my query not from owner
['tracks']['total'] gives you number of tracks

tracks data frame
from tracks items ['added_at'] get the data time the track was added
from tracks items ['track'] get duration_ms as float
for artist in tracks items ['track']['artists'][0]['name'] get the first artist
from tracks items ['track'] get explicit as bool
from tracks items ['track'] get id as string
from tracks items ['track'] get name as string
from tracks items ['track'] get popularity as float (0-100)

"""

def get_plists_tracks():
    """ NOTE: THIS WILL TAKE 8-9 HOURS TO RUN!!!!
    Also, users is a global variable..."""
    for chunk in range(0,8470,10):
        time.sleep(2)
        t0 = time.time()
        for user in users[chunk:chunk+10]:
            try:
                playlists = sp.user_playlists(user, limit=20)
            except:
                continue

            playlist_dict = {'id': [], 'user': [], 'name': [], 'collab': [], 'desc': [], 'num_tracks': [], 'followers': []}
            track_dict = {'id': [], 'playlist_id': [], 'name': [], 'added_at': [], 'duration': [], 'artist': [],\
                                                                              'explicit': [], 'popularity': []}
            try:
                playlists['items']
            except:
                continue
            for playlist in playlists['items']:
                try:
                    play_obj = sp.user_playlist(user=user, playlist_id=playlist['id'])
                except:
                    continue
                try:
                    playlist_dict['id'].append(play_obj['id'])
                    playlist_dict['user'].append(user)
                    playlist_dict['name'].append(play_obj['name'])
                    playlist_dict['collab'].append(play_obj['collaborative'])
                    playlist_dict['desc'].append(play_obj['description'])
                    playlist_dict['followers'].append(play_obj['followers']['total'])
                    playlist_dict['num_tracks'].append(play_obj['tracks']['total'])
                except:
                    continue
                for track in play_obj['tracks']['items']:
                    try:
                        track_dict['added_at'].append(track['added_at'])
                        track_dict['playlist_id'].append(play_obj['id'])
                    except:
                        continue
                    try:
                        track_dict['duration'].append(track['track']['duration_ms'])
                        track_dict['id'].append(track['track']['id'])
                        track_dict['name'].append(track['track']['name'])
                        track_dict['explicit'].append(track['track']['explicit'])
                        track_dict['artist'].append(track['track']['artists'][0]['name'])
                        track_dict['popularity'].append(track['track']['popularity'])
                    except:
                        track_dict['duration'].append(np.NaN)
                        track_dict['id'].append(np.NaN)
                        track_dict['name'].append(np.NaN)
                        track_dict['explicit'].append(np.NaN)
                        track_dict['artist'].append(np.NaN)
                        track_dict['popularity'].append(np.NaN)
        tdf = pd.DataFrame(track_dict)
        pdf = pd.DataFrame(playlist_dict)
        tdf.to_json('dfs/track_part{}.json'.format(chunk))
        pdf.to_json('dfs/plist_part{}.json'.format(chunk))
        print('that took {0} sec for num {1}'.format(time.time()-t0,chunk))

# Running commands
#get_plists_tracks()

# Aggregate mini-dataframes into larger dataframes
plists = pd.read_json('dfs/plist_part0.json')
tracks = pd.read_json('dfs/track_part0.json')

for chunk in range(10,8470,10):
    temp_track = pd.read_json('dfs/track_part{}.json'.format(chunk))
    temp_plist = pd.read_json('dfs/plist_part{}.json'.format(chunk))
    plists = plists.append(temp_plist)
    tracks = tracks.append(temp_track)

# Reset Index
plists.index = pd.RangeIndex(len(plists.index))
tracks.index = pd.RangeIndex(len(tracks.index))

# Save JSON dataframes
# plists.to_json('data/plist_df.json')
# tracks.to_json('data/track_df.json')
