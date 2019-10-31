from .models import SessionSongs
from django.db import connection

def move_track_in_queue(session_id, move_song_id, after_song_id):
    with connection.cursor() as cursor:
        cursor.execute("""UPDATE core_sessionsongs SET next_song_id = 
                         (SELECT s.next_song_id FROM core_sessionsongs s WHERE s.session_id = %s AND s.song_id = %s)
                          WHERE session_id = %s AND song_id =
                         (SELECT b.song_id FROM core_sessionsongs b WHERE b.session_id = %s AND b.next_song_id = %s)
                       """, [session_id, move_song_id, session_id, session_id, move_song_id])

        cursor.execute("""UPDATE core_sessionsongs SET next_song_id = %s
                          WHERE session_id = %s AND song_id = 
                         (SELECT b.song_id FROM core_sessionsongs b WHERE b.session_id = %s AND b.next_song_id = %s)
                       """, [move_song_id, session_id, session_id, after_song_id])
        
        cursor.execute("""UPDATE core_sessionsongs SET next_song_id = %s
                          WHERE session_id = %s AND song_id = %s
                       """, [after_song_id, session_id, move_song_id])