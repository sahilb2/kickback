from .models import SessionSongs

def get_tracks_in_queue(session_id):
    trackList = SessionSongs.objects.raw('SELECT * FROM SessionSongs WHERE session_id = %s', [session_id]) 

    
