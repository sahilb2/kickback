from .models import SessionSongs

def get_tracks_in_queue(session_id):
    trackList = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id = %s', [session_id]) 

    if (len(trackList) == 0):
        return []

    trackIds = {}
    trackUris = []

    currentTrack = None
    for track in trackList:
        trackIds[ track.song_id ] = track
        trackUris.append(track.spotify_uri)
        if (track.is_curr_song):
            currentTrack = track

    # This should be a list of spotify info for each track
    trackListInfo = "SAHIL USE YOUR HELPER FUNCTION HERE!!!!"

    trackInfo = {}
    for track in trackListInfo:
        trackInfo[ track['uri'] ] = track

    sortedTracks = []
    while (currentTrack != None):
        currentTrack.update(trackInfo[ currentTrack.spotify_uri ])
        sortedTracks.append(currentTrack)
        if (currentTrack.next_song_id != None):
            currentTrack = trackIds[ currentTrack.next_song_id ]
        else:
            break

    return sortedTracks


