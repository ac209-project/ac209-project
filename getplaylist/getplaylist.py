import spotipy
import matplotlib.pyplot as plt
import numpy as np

from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id = '99fd6b637f19418996f726efd4f57aa3',
                                                      client_secret='00331cf90a064cafa7223fd9b6c6b8c5')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

user = 'spotify'
limit = 20
playlists = sp.user_playlists(user, limit=limit)
followers = []
names = []
for i, playlist in enumerate(playlists['items']):
    fols = sp.user_playlist(user=user, playlist_id=playlist['id'])
    followers.append(fols['followers']['total'])
    names.append(fols['name'])
    print(fols['name'], fols['followers']['total'])

    if i >= limit:
        break

x = np.arange(len(followers))
plt.bar(x, followers)
plt.xticks(x, names)
plt.legend()
plt.show()