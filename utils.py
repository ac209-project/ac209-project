"""
General utils for streamlining use of spotipy API.
"""
import os

import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


def get_auth_spotipy () -> Spotify:
    """Returns authorized Spotify client."""
    os.environ['SPOTIPY_CLIENT_ID'] = 'f7cddb18358749f79c1a12b4a66f61bb'
    os.environ['SPOTIPY_CLIENT_SECRET'] = '2caf6e49bb55457f9925c6e8874a38c4'

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp
