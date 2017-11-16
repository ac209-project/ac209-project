"""
Examples of basic spotipy functionality.
"""

import pprint

from utils import get_auth_spotipy

section_break = lambda x:'\n{0}\n{1}\n{0}\n'.format('-'*30, x)

sp = get_auth_spotipy()


def muse_search_results ():
    """The results of searching for Muse in Spotify."""
    search_str = 'Muse'
    result = sp.search(search_str)
    pprint.pprint(result)


def user_playlists ():
    """Getting playlists for particular user."""
    user = 'spotify'
    playlists = sp.user_playlists(user)
    for playlist in playlists['items']:
        print(playlist['name'])


def user_playlist ():
    """Retrieving specific playlist info. Prints artists in playlist."""
    user = 'indiefolkradio'
    playlist_id = '1Qs40FRP061tVZ9x2npAE3'
    playlist = sp.user_playlist(user, playlist_id)

    for i, track in enumerate(playlist['tracks']['items']):
        print(section_break('Track {}'.format(i + 1)))
        print('Name: {}'.format(track['track']['name']))
        print('Spotify ID: {}'.format(track['track']['id']))
        print('Album: {}'.format(track['track']['album']['name']))

        # Example of getting track information with the id provided.
        # track_id = track['track']['id']
        # track_info = sp.track(track_id)
        # print(track_info['album']['name'])


user_playlist()
