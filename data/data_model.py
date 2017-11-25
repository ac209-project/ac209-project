"""
Compiling the DataFrame used for EDA / modeling.
"""

import ast

import numpy as np
import pandas as pd

from utils import flatten


#####################################################################
# Loading supporting DataFrames.
#####################################################################

def load_track ():
    track = pd.read_csv('track/track.csv', encoding='ISO-8859-1')
    track.drop_duplicates('id', inplace=True)
    track.set_index('id', inplace=True)
    track['artist_ids'] = track['artist_ids'].apply(ast.literal_eval)
    return track


def load_album ():
    album = pd.read_csv('album/album.csv', encoding='ISO-8859-1')
    album.drop_duplicates('id', inplace=True)
    album.set_index('id', inplace=True)
    return album


def load_artist ():
    df = pd.read_csv('artist/artist.csv', encoding='ISO-8859-1')
    df.drop_duplicates('id', inplace=True)
    df.set_index('id', inplace=True)
    df['genres'] = df['genres'].apply(ast.literal_eval)
    return df


album = load_album()
artist = load_artist()
track = load_track()


#####################################################################
# Build main DataFrame for analysis.
#####################################################################

def album_popularity (playlist_row):
    """Computes average album popularity for playlist.

    Note: An album is weighted once even if it is encountered multiple times.
    """
    try:
        track_ids = playlist_row['track_ids']
        track_rows = track.loc[track_ids]
        album_ids = track_rows['album_id'].tolist()
        album_rows = album.loc[album_ids]
        return album_rows['popularity'].mean()
    except:
        print('Exception at this row:\n\n{}'.format(playlist_row))
        return np.NaN


def artist_popularity (playlist_row):
    """Computes average artist popularity for playlist."""
    track_ids = playlist_row['track_ids']
    track_rows = track.loc[track_ids]
    artist_ids = set(flatten(track_rows['artist_ids'].tolist()))
    artist_rows = artist.loc[artist_ids]
    return artist_rows['popularity'].mean()


def artist_followers (playlist_row):
    """Computes average artist followers for playlist."""
    track_ids = playlist_row['track_ids']
    track_rows = track.loc[track_ids]
    artist_ids = set(flatten(track_rows['artist_ids'].tolist()))
    artist_rows = artist.loc[artist_ids]
    return artist_rows['followers'].mean()


def track_popularity (playlist_row):
    """Computes average track popularity for playlist."""
    track_ids = playlist_row['track_ids']
    track_rows = track.loc[track_ids]
    return track_rows['popularity'].mean()


def load_main_df ():
    """Aggregates information across DataFrames to produce model-ready DF."""
    playlist = pd.read_csv('playlist/playlist.csv', encoding='ISO-8859-1')
    playlist['track_ids'] = playlist['track_ids'].apply(ast.literal_eval)
    playlist['track_pop'] = playlist.apply(track_popularity, axis=1)
    playlist['album_pop'] = playlist.apply(album_popularity, axis=1)
    playlist['artist_pop'] = playlist.apply(artist_popularity, axis=1)
    playlist['artist_followers'] = playlist.apply(artist_followers, axis=1)
    return playlist


if __name__ == '__main__':
    df = load_main_df()
    print(df.head())
