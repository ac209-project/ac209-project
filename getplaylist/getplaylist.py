import spotipy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id = '99fd6b637f19418996f726efd4f57aa3',
                                                      client_secret='00331cf90a064cafa7223fd9b6c6b8c5')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

user = 'spotify'
limit = 10

search_results = sp.search('R*', limit = limit, offset = 0, type = 'playlist')

#print(search_results['playlists']['items'])
playlists = pd.DataFrame.from_dict(search_results['playlists']['items'])


37i9dQZF1DWY7IeIP1cdjF

playlists.to_csv('playlists.csv')
print("Done")
