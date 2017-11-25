"""
Saving the CSVs with data retrieved using Spotify API.
"""

from time import clock

import pandas as pd

from utils import clean_csv_path, flatten, get_auth_spotipy

sp = get_auth_spotipy()  # same client used throughout module to query


def get_album_ids (tracks):
    """Loops through tracks to extract each album:id attribute."""
    album_ids = []
    for track in tracks:
        try:
            album_id = track['album']['id']
            album_ids.append(album_id)
        except:
            pass
    return album_ids


#####################################################################
# Building artist CSV.
#####################################################################

def build_artist_row (artist):
    """Returns dict representing row in artist DataFrame."""
    return {'id':artist['id'],
            'name':artist['name'],
            'genres':artist['genres'],
            'popularity':artist['popularity'],
            'followers':artist['followers']['total']}


#####################################################################
# Building album CSV.
#####################################################################

def build_album_row (album):
    """Returns dict representing row in album DataFrame."""
    artist_ids = [artist['id'] for artist in album['artists']]
    return {'id':album['id'],
            'artist_ids':artist_ids,
            'name':album['name'],
            'genres':album['genres'],
            'popularity':album['popularity'],
            'release_date':album['release_date']}


#####################################################################
# Building track CSV.
#####################################################################

def build_track_row (track):
    """Returns dict representing row in track DataFrame."""
    artist_ids = [artist['id'] for artist in track['artists']]

    return {'id':track['id'],
            'name':track['name'],
            'duration_ms':int(track['duration_ms']),
            'album_id':track['album']['id'],
            'popularity':int(track['popularity']),
            'artist_ids':artist_ids}


#####################################################################
# Building playlist CSV.
#####################################################################

def build_data_from_playlist (plist, user):
    """Extracts all data available from playlist info (without having to make
    additional API queries).

    Rows are made to be added to be added to the tracks DataFrame as well
    because all pertinent information at the track level is included within
    the playlist info, i.e., nothing is gained from making separate calls to
    the sp.track().

    Args:
        plist (dict): Result of making call to user_playlist(). Method will
            break if simply given playlist info resulting from a call to
            sp.user_playlists(user_name, limit=50), which is more limited.
        user (str): User this playlist was retrieved from.

    Returns: tuple
        playlist_row (dict): Row containing metadata for one playlist.
        track_rows (List[dict]): Rows to be appended to track DataFrame,
            with each element in this list containing metadata for one track.
    """
    track_items = plist['tracks']['items']  # list of dicts (one for each track)
    added_at = [item['added_at'] for item in track_items]
    added_by = [item['added_by']['id'] for item in track_items]
    tracks = [item['track'] for item in track_items]
    track_ids = [track['id'] for track in tracks]

    # Build playlist row.
    playlist_row = {'id':plist['id'],
                    'user':user,
                    'followers':int(plist['followers']['total']),
                    'track_count':int(plist['tracks']['total']),
                    'track_ids':track_ids,
                    'track_added_at':added_at,
                    'track_added_by':added_by}

    # Build track rows.
    track_rows = []
    for track in tracks:
        track_rows.append(build_track_row(track))

    # Return everything.
    return playlist_row, track_rows


def build_data (users):
    """Obtains playlist-level metadata.

    Args:
        users (List[str]): List of user_names, each of which will used to
            call sp.user_playlists() to obtain universe of playlists to obtain
            data for.
    """
    # Init DataFrames.
    df_playlist = pd.DataFrame(
          columns=['id', 'user', 'followers', 'track_count', 'track_ids',
                   'track_added_at', 'track_added_by'])
    df_track = pd.DataFrame(
          columns=['id', 'name', 'duration_ms', 'album_id', 'popularity',
                   'artist_ids'])

    # Append data to the two DataFrames for info extracted from playlists.
    plist_count = 0
    for user in users:
        playlists = sp.user_playlists(user)
        for plist in playlists['items']:
            time0 = clock()
            plist_info = sp.user_playlist(user, plist['id'])
            row_plist, rows_track = build_data_from_playlist(plist_info, user)
            df_playlist = df_playlist.append(row_plist, ignore_index=True)
            df_track = df_track.append(rows_track)
            time = (clock() - time0)
            print('Added playlist {0} in {1:.1f}s.'.format(plist_count, time))
            plist_count += 1
            if plist_count > 2:
                break

    # Save playlist and track DFs to CSV.
    # Define file paths to save to.
    playlist_path = clean_csv_path('playlist/playlist')
    track_path = clean_csv_path('track/track')
    df_playlist.to_csv(playlist_path)
    df_track.to_csv(track_path)

    # Build album DataFrame.
    df_album = pd.DataFrame(
          columns=['id', 'artist_ids', 'name', 'genres', 'popularity',
                   'release_date'])
    album_ids = df_track['album_id'].unique().tolist()
    albums = sp.albums(album_ids)
    for album in albums:
        album_row = build_album_row(album)
        df_album = df_album.append(album_row, ignore_index=True)
    album_path = clean_csv_path('album/album')
    df_album.to_csv(album_path)

    # Build artist DataFrame.
    df_artist = pd.DataFrame(
          columns=['id', 'name', 'genres', 'popularity', 'followers'])
    artist_ids = flatten(df_track['artist_ids'].tolist())
    print('Artist ids', artist_ids)

    artists = sp.artists(artist_ids)
    for artist in artists:
        artist_row = build_artist_row(artist)
        df_artist = df_artist.append(artist_row, ignore_index=True)
    artist_path = clean_csv_path('artist/artist')
    df_artist.to_csv(artist_path)


#####################################################################
# Building data for all usernames.
#####################################################################

if __name__ == '__main__':
    users = ['bedburger', 'buzzfeed']
    build_data(users)
