"""
General utils for streamlining use of spotipy API.
"""
import os
import pandas as pd
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import copy
import datetime

def explode_value(df_in, col1, col2=None):
    """ This function is used when you have a list or two in your pandas
    dataframe and you want to 'explode' (like the Hive feature out the
    dataframe so your list now has a row for every element.
    ------------
    Example:        col1    col2    col3
                0   'mike'   [12,8]  ['dog','cat']
                1   'lucy'   [9,44]  ['mouse','lemon']
                ...
                explode_value(df, 'col2', 'col3')
    Example:        col1    col2    col3
                0   'mike'   12      'dog'
                1   'mike'   8       'cat'
                2   'lucy'   9       'mouse'
                3   'lucy'   44      'lemon'
    -----------
    Args: df_in; Pandas Dataframe that contains the columns as lists that
            you want to explode out.
          col1; string name of the column that you want to explode out.
          col2; string name of the second column that you want to explode
            out.  (optional argument)
    -----------
    Returns: Pandas Dataframe that is exploded out by your chosen column(s)
    -----------
    Raises: ValueError in the case you do not input a dataframe or you have
        columns with different lengths to blow out.
    """
    if not isinstance(df_in, pd.DataFrame):
        raise ValueError('You did not input a DataFrame.')
    new_obs = []
    if col2:
        # Case where col2 is passed
        for row in df_in.to_dict(orient='records'):
            breakout_col1= row[col1]
            breakout_col2 = row[col2]
            if len(breakout_col1)!= len(breakout_col2):
                raise ValueError('{0} and {1} are not the same length in row {2}'.format(col1,col2,row))
            del row[col1]
            del row[col2]
            for c1, c2 in zip(breakout_col1, breakout_col2):
                new_obs_row = copy.deepcopy(row)
                new_obs_row[col1] = c1
                new_obs_row[col2] = c2
                new_obs.append(new_obs_row)
        df_out = pd.DataFrame(new_obs)
        return df_out
    else:
        # Case where col2 is omitted
        for row in df_in.to_dict(orient='records'):
            breakout_col1= row[col1]
            if not isinstance(breakout_col1, list):
                print('Warning: The object | {0} | you are exploding out is not a list.'.format(breakout_col1))
            del row[col1]
            for c1 in breakout_col1:
                new_obs_row = copy.deepcopy(row)
                new_obs_row[col1] = c1
                new_obs.append(new_obs_row)
        df_out = pd.DataFrame(new_obs)
        return df_out



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
    w2v = pd.read_json('data/w2v_feature.json')
    # artist_genres['artist_genre'] = [tuple(g) if g else () for g in artist_genres['artist_genre']]

    # plists = plists.rename(columns={'name': 'playlist_name','id': 'playlist_id'})
    plists = plists.rename(columns = {'name':'pl_name', 'id':'pl_id', 'followers':'pl_followers',
                          'num_tracks':'pl_num_trks', 'user':'pl_owner',
                         'desc':'pl_desc'})
    # tracks = tracks.rename(columns={'id': 'track_id','name':'track_name','popularity': 'track_pop'})
    tracks = tracks.rename(columns = {'name':'trk_name', 'id':'trk_id',
                            'playlist_id':'pl_id', 'artist':'art_name',
                            'popularity':'trk_popularity', 'added_at':'trk_added_at',
                           'duration':'trk_duration'})
    user_followers = user_followers.rename(columns={'user': 'pl_owner'})
    artist_genres = artist_genres.rename(columns={'artist': 'art_name'})
    # Merging
    temp1 = pd.merge(tracks,artist_genres,how='left',on='art_name')
    temp2 = pd.merge(temp1,plists,how='left',on='pl_id')
    temp3 = pd.merge(temp2,w2v,how='left',on='pl_id')
    df_trk = pd.merge(temp3,user_followers,how='left',on='pl_owner')

    df_trk = df_trk.dropna(subset = ['trk_popularity', 'pl_followers'])

    # Data wrangling - additional track-level and playlist-level features

    # Oldest and newest date that a track was added to the playlist
    df_trk['pl_first_date'] = df_trk.groupby('pl_id')['trk_added_at'].transform('min')
    df_trk['pl_last_date'] = df_trk.groupby('pl_id')['trk_added_at'].transform('max')
    df_trk['pl_days_active'] = (df_trk['pl_last_date'] - df_trk['pl_first_date']).astype('timedelta64[D]')
    df_trk['pl_days_old'] = (datetime.datetime.now() - df_trk['pl_first_date']).astype('timedelta64[D]')

    # Number of tracks in the playlist
    df_trk['pl_num_trk'] = df_trk.groupby('pl_id')['trk_id'].transform('count')

    # Number of artists in the playlist
    df_trk['pl_num_art'] = df_trk.groupby('pl_id')['art_name'].transform('nunique')

    # Max, min, and average track popularity (by playlist)
    df_trk['pl_min_trkpop'] = df_trk.groupby('pl_id')['trk_popularity'].transform('min')
    df_trk['pl_max_trkpop'] = df_trk.groupby('pl_id')['trk_popularity'].transform('max')
    df_trk['pl_mean_trkpop'] = df_trk.groupby('pl_id')['trk_popularity'].transform('mean')

    df_trk['art_min_trkpop'] = df_trk.groupby('art_name')['trk_popularity'].transform('min')
    df_trk['art_max_trkpop'] = df_trk.groupby('art_name')['trk_popularity'].transform('max')
    df_trk['art_mean_trkpop'] = df_trk.groupby('art_name')['trk_popularity'].transform('mean')
    df_trk['art_total_trks'] = df_trk.groupby('art_name')['trk_name'].transform('nunique').astype('int')

    # Add a label category for each artist (currently just 5 labels but could be expanded)
    df_trk['art_class'] = ""
    df_trk.loc[(df_trk.art_mean_trkpop>=50) & (df_trk.art_total_trks>=10), 'art_class'] = 'superstar'
    df_trk.loc[(df_trk.art_mean_trkpop>=20) & (df_trk.art_mean_trkpop<50) & (df_trk.art_total_trks>=10), 'art_class'] = 'star'
    df_trk.loc[(df_trk.art_mean_trkpop>=0) & (df_trk.art_mean_trkpop<20) & (df_trk.art_total_trks>=10), 'art_class'] = 'crap_factory'
    df_trk.loc[(df_trk.art_mean_trkpop>=40) & (df_trk.art_total_trks<10), 'art_class'] = 'one_hit_wonder'
    df_trk.loc[(df_trk.art_mean_trkpop<40) & (df_trk.art_total_trks<10), 'art_class'] = 'garage_band'
    df_trk['art_class'] = pd.Categorical(df_trk['art_class'], categories=["superstar","star","crap_factory", "one_hit_wonder", "garage_band"])

    # Fix followers to int
    df_trk['pl_followers'] = df_trk.loc[:,'pl_followers'].astype('int')

    # Number of playlists per user
    df_trk['user_pls_in_sample'] = df_trk.groupby('pl_owner')['pl_id'].transform('count')

    # Size number of characters in the playlist description
    df_trk['pl_desc_chars'] = df_trk.pl_desc.str.len().fillna(0).astype('int')
    return df_trk

def get_auth_spotipy () -> Spotify:
    """Returns authorized Spotify client."""
    os.environ['SPOTIPY_CLIENT_ID'] = 'f7cddb18358749f79c1a12b4a66f61bb'
    os.environ['SPOTIPY_CLIENT_SECRET'] = '2caf6e49bb55457f9925c6e8874a38c4'

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def load_celebs_df(lcase=False):
    """Lowercase celeb names because """
    df = pd.read_csv('data/celebs.csv', encoding='latin')
    if lcase:
        df['name'] = df['name'].apply(str.lower)
    return df
