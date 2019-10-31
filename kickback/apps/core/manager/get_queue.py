from kickback.apps.core.models import User, SessionSongs
from kickback.apps.core.manager.helper import batch_get_track_from_uri, convert_spotify_track_to_kickback_track

def get_tracks_in_queue(session_id):
    track_list = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id_id = %s', [session_id])

    if len(track_list) == 0:
        return []

    track_ids = {}
    track_uri_list = []

    current_track = None
    for track in track_list:
        track_ids[track.song_id] = track
        track_uri_list.append(track.spotify_uri)
        if (track.is_curr_song):
            current_track = track

    spotify_track_list_info = batch_get_track_from_uri(track_uri_list)
    track_list_info = list(map(convert_spotify_track_to_kickback_track, spotify_track_list_info['tracks']))

    track_info = {}
    for track in track_list_info:
        track_info[track['uri']] = track

    sorted_tracks = []
    while current_track is not None:
        current_track_info = {}
        current_track_info['song_id'] = current_track.song_id
        current_track_info['username'] = User.objects.raw('SELECT * FROM core_user WHERE user_id = %s', [current_track.user_id])[0].username
        current_track_info.update(track_info[current_track.spotify_uri])
        sorted_tracks.append(current_track_info)
        current_track = track_ids.get(current_track.next_song_id)

    return sorted_tracks
