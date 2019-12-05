from kickback.apps.core.models import SessionSongs, CurrentSongs
from kickback.apps.core.manager.sockets import call_socket_for_update_queue
from kickback.apps.core.manager.chat import add_to_chat_for_session
from kickback.apps.core.manager.helper import batch_get_track_from_uri, convert_spotify_track_to_kickback_track
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

def create_add_song_chat_message(song_name, username):
    return str(username) + ' added song ' + str(song_name) + ' to the queue.'

def trigger_add_song_message_to_chat(session_id, spotify_uri, username):
    spotify_track = batch_get_track_from_uri([spotify_uri])['tracks'][0]
    song_name = convert_spotify_track_to_kickback_track(spotify_track)['name']
    message = create_add_song_chat_message(song_name, username)
    add_to_chat_for_session(session_id, message, 'Kickback')

@transaction.atomic
def add_track_in_queue(session_id, spotify_uri, username):
    last_song_query_results = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id = %s AND next_song_id IS NULL', [session_id])
    if len(last_song_query_results) > 1:
        return HttpResponseServerError('More than 1 last song found...')

    with connection.cursor() as cursor:
        # Insert new song
        cursor.execute('INSERT INTO core_sessionsongs(session_id, spotify_uri, username) VALUES (%s, %s, %s)',
            [session_id, spotify_uri, username])

        # Get song_id of the newly added song
        new_last_song_id = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id = %s ORDER BY song_id DESC LIMIT 1', [session_id])[0].song_id

        if len(last_song_query_results) == 1:
            # Update old last song's next_song_id
            last_song_id = last_song_query_results[0].song_id
            cursor.execute('UPDATE core_sessionsongs SET next_song_id = %s WHERE song_id = %s', [new_last_song_id, last_song_id])
        else:
            # New song is the only song in the queue, so make it the current song
            cursor.execute('INSERT INTO core_currentsongs(session_id, song_id) VALUES (%s, %s)', [session_id, new_last_song_id])

    call_socket_for_update_queue(session_id)

    trigger_add_song_message_to_chat(session_id, spotify_uri, username)

    return HttpResponse('Song added with song_id: ' + str(new_last_song_id))
