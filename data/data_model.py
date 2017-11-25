"""
Compiling the DataFrame used for EDA / modeling.
"""

from ast import literal_eval
import sqlite3

import numpy as np
import pandas as pd

from utils import flatten

CONN = sqlite3.connect('spotify_db.sqlite')


#####################################################################
# Loading supporting DataFrames.
#####################################################################

def load_track ():
    df = pd.read_sql('SELECT * FROM track', CONN)
    df.drop_duplicates('id', inplace=True)
    df.set_index('id', inplace=True)
    df['artist_ids'] = df['artist_ids'].apply(literal_eval)
    return df


def load_album ():
    df = pd.read_sql('SELECT * FROM album', CONN)
    df.drop_duplicates('id', inplace=True)
    df.set_index('id', inplace=True)
    df['artist_ids'] = df['artist_ids'].apply(literal_eval)
    df['release_date'] = pd.to_datetime(df['release_date'])
    return df


def load_artist ():
    df = pd.read_sql('SELECT * FROM artist', CONN)
    df.drop_duplicates('id', inplace=True)
    df.set_index('id', inplace=True)
    df['genres'] = df['genres'].apply(literal_eval)
    return df


def load_playlist ():
    df = pd.read_sql('SELECT * FROM playlist', CONN)
    df['track_ids'] = df['track_ids'].apply(literal_eval)
    df['track_added_at'] = df['track_added_at'].apply(literal_eval)
    df.set_index('id', inplace=True)
    return df


# Load supporting DFs, which are used in calculating metrics below.
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


def build_analysis_df ():
    """Aggregates information across DataFrames to produce model-ready DF."""
    df = load_playlist()
    df['track_pop'] = df.apply(track_popularity, axis=1)
    df['album_pop'] = df.apply(album_popularity, axis=1)
    df['artist_pop'] = df.apply(artist_popularity, axis=1)
    df['artist_followers'] = df.apply(artist_followers, axis=1)
    return df


if __name__ == '__main__':
    df = build_analysis_df()
    print(df.head())

