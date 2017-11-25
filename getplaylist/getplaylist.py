import spotipy
import numpy as np
import pandas as pd
import string
from spotipy.oauth2 import SpotifyClientCredentials

# Set up oath
client_credentials_manager = SpotifyClientCredentials(client_id = '99fd6b637f19418996f726efd4f57aa3',
                                                      client_secret='00331cf90a064cafa7223fd9b6c6b8c5')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Fixed system parameters:
limit = 50 # Maximum number of playlists per search
user_names = set() # Output of user names returned

# Total number of searches to perform:
first_letters = string.ascii_lowercase + string.ascii_uppercase
#first_letters = "ABCDE"
passes_per_letter = 20 # Number of 50-df searches per alphabet letter
starting_offset = 0
ending_offset = starting_offset + passes_per_letter*limit+1

# Search for lists of playlists of size [limit] for each letter in the full ASCII alphabet
for offset in range(starting_offset, ending_offset, limit):
    for first_letter in first_letters:
        playlists = sp.search(first_letter+'*', limit = limit, offset = offset, type = 'df')

        for playlist in playlists['playlists']['items']:
            user_names.add(playlist['owner']['id'])

    print("\nCompleted offset = {}.  Total unique users found:{}".format(offset, len(user_names)))

print("API pull complete - obtained a total of {} user names!".format(len(user_names)))

with open('offset_{}_{}.txt'.format(starting_offset, ending_offset+limit-1),
          "w", encoding='utf-8') as output:
    for item in user_names:
        output.write("{}\n".format(item))