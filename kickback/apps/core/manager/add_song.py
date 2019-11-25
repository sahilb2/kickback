from kickback.apps.core.models import SessionSongs
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

@transaction.atomic
def add_track_in_queue(session_id, spotify_uri, user_id):
    last_song_query_results = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id = %s AND next_song_id IS NULL', [session_id])

    if len(last_song_query_results) > 1:
        return HttpResponseServerError('More than 1 last song found...')

    # No last song, add this song and make it the current song
    with connection.cursor() as cursor:

        # Set is_curr_song to True if this is the only song in the queue, meaning no last song is found
        is_curr_song = 'TRUE' if len(last_song_query_results) == 0 else 'FALSE'

        cursor.execute('INSERT INTO core_sessionsongs(session_id, spotify_uri, user_id, is_curr_song) VALUES (%s, %s, %s, %s)',
            [session_id, spotify_uri, user_id, is_curr_song])

        if len(last_song_query_results) == 1:
            # Update old last song's next
            last_song_id = last_song_query_results[0].song_id
            new_last_song_id = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id = %s ORDER BY song_id DESC LIMIT 1', [session_id])[0].song_id

            cursor.execute('UPDATE core_sessionsongs SET next_song_id = %s WHERE song_id = %s', [new_last_song_id, last_song_id])

    return HttpResponse('Song added!')
