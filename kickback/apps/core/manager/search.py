from kickback.apps.core.manager.helper import search_tracks_by_query_helper, convert_spotify_track_to_kickback_track

def search_tracks_by_query(track_query):
    results = search_tracks_by_query_helper(track_query)
    tracks = results['tracks']['items']
    tracks_list = []
    for track in tracks:
        tracks_list.append(convert_spotify_track_to_kickback_track(track))
    return tracks_list
