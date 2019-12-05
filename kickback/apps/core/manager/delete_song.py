from kickback.apps.core.models import SessionSongs
from kickback.apps.core.manager.sockets import call_socket_for_update_queue
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseBadRequest

@transaction.atomic
def delete_track_in_queue(song_id):
    song_to_be_deleted_query = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE song_id = %s', [song_id])

    if len(song_to_be_deleted_query) != 1:
        return HttpResponseBadRequest('Invalid song_id. Enter valid song_id to delete a song.')

    song_to_be_deleted = song_to_be_deleted_query[0]

    session_id = song_to_be_deleted.session_id
    song_id_after = song_to_be_deleted.next_song_id

    song_before_query = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE next_song_id = %s', [song_id])

    if len(song_before_query) != 1:
        return HttpResponseBadRequest('Invalid song_id. No songs before this in the queue. You cannot DELETE the current song.')

    song_before_id = song_before_query[0].song_id

    with connection.cursor() as cursor:
        cursor.execute("""UPDATE core_sessionsongs
                          SET next_song_id = %s
                          WHERE song_id = %s
                       """, [song_id_after, song_before_id])

        cursor.execute("""DELETE FROM core_sessionsongs
                          WHERE song_id = %s
                       """, [song_id])

    call_socket_for_update_queue(session_id)

    return HttpResponse('Deleted song!')
