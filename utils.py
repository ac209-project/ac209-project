"""
General utils for streamlining use of spotipy API.
"""
import os
import pandas as pd
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import copy

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
