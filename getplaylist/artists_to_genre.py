import numpy as np
import pandas as pd
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# Set up oath
client_credentials_manager = SpotifyClientCredentials(client_id = '99fd6b637f19418996f726efd4f57aa3',
                                                      client_secret='00331cf90a064cafa7223fd9b6c6b8c5')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Get artists
tracks = pd.read_json('../data/track_df.json')
artists = tracks['artist'].drop_duplicates()

# Get user followers for each user

def get_artists_genres():
    """ NOTE: THIS WILL TAKE 6-7 HOURS TO RUN!!!!
    Also, artists is a global variable..."""
    artist_dict = {'artist': [], 'artist_id': [], 'artist_followers': [],'artist_pop': [],\
                                                                       'artist_genre': []}
    for i,artist in enumerate(artists):
        if i < 8001:
            continue
        if i % 1001 == 0:
            t0 = time.time()
        try:
            a = sp.search(artist,type='artist')
        except:
            continue

        artist_dict['artist'].append(artist)
        try:
            artist_dict['artist_id'].append(a['artists']['items'][0]['id'])
        except:
            artist_dict['artist_id'].append(np.NaN)
        try:
            artist_dict['artist_followers'].append(a['artists']['items'][0]['followers']['total'])
        except:
            artist_dict['artist_followers'].append(np.NaN)
        try:
            artist_dict['artist_pop'].append(a['artists']['items'][0]['popularity'])
        except:
            artist_dict['artist_pop'].append(np.NaN)
        try:
            if a['artists']['items'][0]['genres']==[]:
                artist_dict['artist_genre'].append(np.NaN)
            else:
                artist_dict['artist_genre'].append(a['artists']['items'][0]['genres'])
        except:
            artist_dict['artist_genre'].append(np.NaN)

        if i % 1000 == 0 and i >0:
            adf = pd.DataFrame(artist_dict)
            try:
                adf.to_json('artists_genre{}.json'.format(i))
            except:
                adf.index = pd.RangeIndex(len(adf.index))
                adf.to_json('artists_genre{}.json'.format(i))
            print('that took {0} sec for num {1}'.format(time.time()-t0,i))

get_artists_genres()
