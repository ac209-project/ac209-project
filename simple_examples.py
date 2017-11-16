"""
Examples of basic spotipy functionality.
"""

import pprint

from utils import get_auth_spotipy

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

muse_search_results()