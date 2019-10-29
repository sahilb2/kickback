import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def search_tracks_by_query(track_query):
    results = spotify.search(q=track_query, type='track', market='US')
    tracks = results['tracks']['items']
    tracks_list = []
    for track in tracks:
        curr_track_info = {}
        curr_track_info['name'] = track['name']
        curr_track_info['uri'] = track['uri']
        # Store artist names
        artists = track['artists']
        artist_name_list = []
        for artist in artists:
            curr_artist_name = artist['name']
            artist_name_list.append(curr_artist_name)
        curr_track_info['artists'] = artist_name_list
        # Store album name
        curr_track_info['album'] = track['album']['name']
        tracks_list.append(curr_track_info)
    return tracks_list
