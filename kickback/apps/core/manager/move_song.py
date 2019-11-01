from kickback.apps.core.models import SessionSongs
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

@transaction.atomic
def move_track_in_queue(move_song_id, after_song_id):
    move_song_query = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE song_id = %s', [move_song_id])

    if len(move_song_query) != 1:
        return HttpResponseBadRequest('Move song not found. Enter valid move_song_id.')

    move_song = move_song_query[0]

    if move_song.is_curr_song:
        return HttpResponseBadRequest('Move song is the current song. Cannot move the current song.')

    prev_move_song_query = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE next_song_id = %s', [move_song_id])

    if len(prev_move_song_query) != 1:
        HttpResponseServerError('Did not find exactly one song before move_song.')

    prev_move_song_id = prev_move_song_query[0].song_id

    if after_song_id is not None:
        after_song_query = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE song_id = %s', [after_song_id])

        if len(after_song_query) != 1:
            return HttpResponseBadRequest('After song not found. Enter valid after_song_id.')

        after_song = after_song_query[0]

        if after_song.is_curr_song:
            return HttpResponseBadRequest('After song cannot be the current song. You cannot move a song before the current song.')

        after_song_id = after_song.song_id

        prev_after_song_query = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE next_song_id = %s', [after_song_id])

        if len(prev_after_song_query) != 1:
            HttpResponseServerError('Did not find exactly one song before after_song.')

        prev_after_song_id = prev_after_song_query[0].song_id

    else:
        prev_after_song_query = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id_id = %s AND next_song_id IS NULL', [move_song.session_id_id])

        if len(prev_after_song_query) != 1:
            HttpResponseServerError('Did not find exactly one song at the end.')

        prev_after_song_id = prev_after_song_query[0].song_id

    with connection.cursor() as cursor:
        cursor.execute("""UPDATE core_sessionsongs
                          SET next_song_id = %s
                          WHERE song_id = %s
                       """, [move_song.next_song_id, prev_move_song_id])

        cursor.execute("""UPDATE core_sessionsongs
                          SET next_song_id = %s
                          WHERE song_id = %s
                       """, [after_song_id, move_song_id])

        cursor.execute("""UPDATE core_sessionsongs
                          SET next_song_id = %s
                          WHERE song_id = %s
                       """, [move_song_id, prev_after_song_id])

    return HttpResponse('Moved song!')
