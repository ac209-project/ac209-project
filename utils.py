"""
General utils for streamlining use of spotipy API, saving data, etc.
"""
from itertools import chain
import os

import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


def get_auth_spotipy () -> Spotify:
    """Returns authorized Spotify client."""
    client_credentials_manager = SpotifyClientCredentials(
          client_id='f7cddb18358749f79c1a12b4a66f61bb',
          client_secret='2caf6e49bb55457f9925c6e8874a38c4')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp


def flatten (iterable):
    """Returns list of elements in iterable flattened by one hierarchy level
    down.

    Example:
        flatten( ( ('A','B','C'), ('D', 'E') ) = ['A','B','C','D','E']
    """
    return [x for x in chain.from_iterable(iterable)]


def clean_csv_path (path):
    """Ensures path is a valid str for a CSV file path by ensuring that it:
    *   Contains .csv extension and
    *   Doesn't already exist. If it does, append int to make it a
        unique file name.
    """
    # ensure path contains csv extension
    if path[-4:] != '.csv':
        path += '.csv'
    # ensure path doesn't already exist
    if os.path.exists(path):
        path_without_ext = path[:-4]
        version_count = 1
        while os.path.exists(path):
            path = path_without_ext + str(version_count) + '.csv'
    return path
