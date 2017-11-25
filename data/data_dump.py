"""
Saving the CSVs with data retrieved using Spotify API.
"""

import pandas as pd

from utils import ProgramTimer, chunks, clean_csv_path, flatten, \
    get_auth_spotipy

log = ProgramTimer(ud_start=True, ud_end=False)
sp = get_auth_spotipy()  # same client used throughout module to query


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
    the playlist info, block_count.e., nothing is gained from making separate
    calls to
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
    tracks = [item['track'] for item in track_items]
    track_ids = [track['id'] for track in tracks]

    # Build playlist row.
    playlist_row = {'id':plist['id'],
                    'user':user,
                    'followers':int(plist['followers']['total']),
                    'track_count':int(plist['tracks']['total']),
                    'track_ids':track_ids,
                    'track_added_at':added_at}

    # Build track rows.
    track_rows = []
    for track in tracks:
        track_rows.append(build_track_row(track))

    # Return everything.
    return playlist_row, track_rows


def build_data (users):
    """Saves four DataFrames produced from results of calling
    sp.user_playlists() on each element of users:
    *   album
    *   artist
    *   playlist
    *   track

    Args:
        users (List[str]): List of user_names, each of which will used to
            call sp.user_playlists() to obtain universe of playlists to obtain
            data for.
    """
    # Init DataFrames.
    df_playlist = pd.DataFrame(
          columns=['id', 'user', 'followers', 'track_count', 'track_ids',
                   'track_added_at'])
    df_track = pd.DataFrame(
          columns=['id', 'name', 'duration_ms', 'album_id', 'popularity',
                   'artist_ids'])

    # Append data to the two DataFrames for info extracted from playlists.
    plist_count = 0
    for user in users:
        try:
            playlists = sp.user_playlists(user)
        except Exception as e:
            log.log_err('sp.user_playlists()', user, str(e))
            continue
        for plist in playlists['items']:
            try:
                plist_info = sp.user_playlist(user, plist['id'])
                row_plist, rows_track = build_data_from_playlist(plist_info,
                                                                 user)
            except Exception as e:
                log.log_err('Adding playlist.', user, str(e))
            else:
                df_playlist = df_playlist.append(row_plist, ignore_index=True)
                df_track = df_track.append(rows_track, ignore_index=True)
            finally:
                plist_count += 1

    # Save playlist, track, album and artist CSVs.

    log.start('Saving playlist')
    print(df_playlist.head())
    playlist_path = clean_csv_path('playlist/playlist')
    df_playlist.to_csv(playlist_path)
    log.end()

    log.start('Saving track')
    df_track.drop_duplicates('id', inplace=True)
    df_track.set_index('id', drop=True, inplace=True)
    track_path = clean_csv_path('track/track')
    df_track.to_csv(track_path)
    log.end()

    log.start('Saving album')
    df_album = pd.DataFrame(
          columns=['id', 'artist_ids', 'name', 'popularity', 'release_date'])
    album_ids = df_track['album_id'].unique().tolist()
    album_ids = [id for id in album_ids if id is not None]
    # Break up albums into chunks.
    for album_id_chunk in chunks(album_ids, 10):
        albums = sp.albums(album_id_chunk)['albums']
        for album in albums:
            album_row = build_album_row(album)
            df_album = df_album.append(album_row, ignore_index=True)
    df_album.drop_duplicates('id', inplace=True)
    df_album.set_index('id', drop=True, inplace=True)
    album_path = clean_csv_path('album/album')
    df_album.to_csv(album_path)
    log.end()

    log.start('Saving artist')
    df_artist = pd.DataFrame(
          columns=['id', 'name', 'genres', 'popularity', 'followers'])
    artist_ids = set(flatten(df_track['artist_ids'].tolist()))
    artist_ids = [id for id in artist_ids if id is not None]
    for artist_id_chunk in chunks(artist_ids, 10):
        artists = sp.artists(artist_id_chunk)['artists']
        for artist in artists:
            artist_row = build_artist_row(artist)
            df_artist = df_artist.append(artist_row, ignore_index=True)
    df_artist.drop_duplicates('id', inplace=True)
    df_album.set_index('id', drop=True, inplace=True)
    artist_path = clean_csv_path('artist/artist')
    df_artist.to_csv(artist_path)
    log.end()


#####################################################################
# Building data for all usernames.
#####################################################################

if __name__ == '__main__':
    BLOCK_SIZE = 1  # number of usernames to process per CSV-save round
    MAX_BLOCKS = 2

    # Load usernames from file.
    with open('..\getplaylist\offset_0_1050.txt', 'r',
              encoding='ISO-8859-1') as f:
        users = [line.replace('\n', '') for line in f]

    # Build data in chunks.
    block_count = 0
    for user_chunk in chunks(users, BLOCK_SIZE):
        log.start('Building data block {}'.format(block_count))
        try:
            build_data(user_chunk)
        except Exception as e:
            log.log_err('build_data(user_chunk)', user_chunk, str(e))
        finally:
            log.end()
            block_count += 1
            if block_count >= MAX_BLOCKS:
                break

    log.print_summary('Finished building data')
    # Save error log.
    errlog_path = clean_csv_path('Error Log')
    log.errors.to_csv(errlog_path)
