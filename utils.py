"""
General utils for streamlining use of spotipy API.
"""
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
