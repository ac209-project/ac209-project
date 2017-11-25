"""
Examples of basic spotipy functionality.
"""

from pprint import pprint

from utils import get_auth_spotipy

section_break = lambda x:'\n{0}\n{1}\n{0}\n'.format('-'*30, x)

sp = get_auth_spotipy()


def muse_search_results ():
    """The results of searching for Muse in Spotify."""
    search_str = 'Muse'
    result = sp.search(search_str)
    pprint(result)


def display_album_info ():
    print('Example album info:\n')
    album_id = 'spotify:album:25BOg6qaiMPRhQwBTWTx9m'
    album_info = sp.album(album_id)
    pprint(album_info)


def display_track_info():
    track_info = sp.track(track_id='3siScYsjnaHdiHOuUcpHTq')
    pprint(track_info)

def user_playlists ():
    """Getting spotify_playlists for particular user."""
    user = 'spotify'
    playlists = sp.user_playlists(user)
    for playlist in playlists['items']:
        print(playlist['name'])

def display_artist_info():
    """Display artist info for Caitlin Rose."""
    artist_info = sp.artist(artist_id='41LGTx1fpA69G2ZAJKZntM')
    pprint(artist_info)


def user_playlist ():
    """Retrieving specific df info. Prints artists in df."""
    user = 'indiefolkradio'
    playlist_id = '1Qs40FRP061tVZ9x2npAE3'
    playlist = sp.user_playlist(user, playlist_id)

    for i, track in enumerate(playlist['tracks']['items']):
        print(section_break('Track {}'.format(i + 1)))
        print('Name: {}'.format(track['track']['name']))
        print('Spotify ID: {}'.format(track['track']['id']))
        print('Album: {}'.format(track['track']['album_info']['name']))
        first_artist_info = track['track']['album_info']['artists'][0]
        print('First Artist Info:'.format())
        artist = sp.artist(first_artist_info['id'])
        print('\tName: {}'.format(artist['name']))
        print('\tTotal followers: {}'.format(artist['followers']['total']))
        print('\tGenres: {}'.format(artist['genres']))

        # Example of getting track information with the id provided.
        # track_id = track['track']['id']
        # track_info = sp.track(track_id)
        # print(track_info['album_info']['name'])


if __name__ == '__main__':
    display_track_info()
