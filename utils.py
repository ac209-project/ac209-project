"""
General utils for streamlining use of spotipy API.
"""
import os
import pandas as pd
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials



def make_working_df():
    """ This utility will make the working copy of the dataframe (i.e takes care of the importing and merging).
    --------
    Args: None
    --------
    Returns: Working version of the dataframe
    ========
    Examples:
    >>> make_working_df()

    --------
    NOTE: DO NOT CHANGE THE NAMES OR LOCATIONS OF OUR BASE JSON DATAFRAMES!!!!
    """
    # Import dataframes
    plists = pd.read_json('data/plist_df.json')
    tracks = pd.read_json('data/track_df.json')
    user_followers = pd.read_json('data/user_follow.json')
    artist_genres = pd.read_json('data/artist_genres_df.json')
    artist_genres['artist_genre'] = [tuple(g) if g else () for g in artist_genres['artist_genre']]

    plists = plists.rename(columns={'name': 'playlist_name','id': 'playlist_id'})
    tracks = tracks.rename(columns={'id': 'track_id','name':'track_name','popularity': 'track_pop'})
    # Merging
    temp1 = pd.merge(tracks,artist_genres,how='left',on='artist')
    temp2 = pd.merge(temp1,plists,how='left',on='playlist_id')
    final_df = pd.merge(temp2,user_followers,how='left',on='user')

    return final_df

def get_auth_spotipy () -> Spotify:
    """Returns authorized Spotify client."""
    os.environ['SPOTIPY_CLIENT_ID'] = 'f7cddb18358749f79c1a12b4a66f61bb'
    os.environ['SPOTIPY_CLIENT_SECRET'] = '2caf6e49bb55457f9925c6e8874a38c4'

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp
