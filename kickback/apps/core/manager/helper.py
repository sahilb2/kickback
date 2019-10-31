import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def search_tracks_by_query_helper(track_query):
    return spotify.search(q=track_query, type='track', market='US')

def batch_get_track_from_uri(uri_list):
    return spotify.tracks(uri_list)

def convert_spotify_track_to_kickback_track(track):
    track_info = {}
    track_info['name'] = track['name']
    track_info['uri'] = track['uri'][-22:]
    # Store artist names
    artists = track['artists']
    artist_name_list = []
    for artist in artists:
        curr_artist_name = artist['name']
        artist_name_list.append(curr_artist_name)
    track_info['artists'] = artist_name_list
    # Store album name
    track_info['album'] = track['album']['name']
    try:
        # Get the 300 by 300 pixels album image
        album_image = track['album']['images'][1]['url']
    except:
        album_image = ''
    track_info['album_image'] = album_image
    return track_info

def is_string_valid(s):
    return not(s is None or s == '')
