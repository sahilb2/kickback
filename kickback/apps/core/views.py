from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.http import require_http_methods
from django.db import transaction, connection
import json
from kickback.apps.core.manager.helper import is_string_valid
from kickback.apps.core.manager.search import search_tracks_by_query
from kickback.apps.core.manager.get_queue import get_tracks_in_queue
from kickback.apps.core.manager.move_song import move_track_in_queue
from kickback.apps.core.manager.delete_song import delete_track_in_queue

from .models import User, Sessions, SessionSongs

def index(request):
    return HttpResponse('Team Frabric presents Kickback Backend!')

def search(request):
    query = request.GET.get('q')
    if query is None or query == '':
        return HttpResponseBadRequest('Use parameter \'q\' to specify query for the search')
    tracks = search_tracks_by_query(query)
    return HttpResponse(json.dumps(tracks), content_type='application/json')

@transaction.atomic
def add_song(request):
    session_id = request.GET.get('session_id')
    spotify_uri = request.GET.get('uri')
    user_id = request.GET.get('user_id')
    if not (is_string_valid(session_id) and is_string_valid(spotify_uri) and is_string_valid(user_id)):
        return HttpResponseBadRequest('Use paramter \'session_id\' to specify session_id,' +
         '\'uri\' to specify the Spotify URI of the track, and \'user_id\' to specify username of the user who added the song')
    last_song_query_results = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id_id = %s AND next_song_id IS NULL', [session_id])
    if len(last_song_query_results) > 1:
        return HttpResponseServerError('More than 1 last song found...')
    # No last song, add this song and make it the current song
    with connection.cursor() as cursor:
        # Set is_curr_song to True if this is the only song in the queue, meaning no last song is found
        is_curr_song = 'TRUE' if len(last_song_query_results) == 0 else 'FALSE'
        cursor.execute('INSERT INTO core_sessionsongs(session_id_id, spotify_uri, user_id, is_curr_song) VALUES (%s, %s, %s, %s)',
            [session_id, spotify_uri, user_id, is_curr_song])
        if len(last_song_query_results) == 1:
            # Update old last song's next
            last_song_id = last_song_query_results[0].song_id
            new_last_song_id = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE session_id_id = %s ORDER BY song_id DESC LIMIT 1', [session_id])[0].song_id
            cursor.execute('UPDATE core_sessionsongs SET next_song_id = %s WHERE song_id = %s', [new_last_song_id, last_song_id])
    return HttpResponse('Song added!')

def move_song(request):
    move_song_id = request.GET.get('move_song_id')
    after_song_id = request.GET.get('after_song_id')
    if not is_string_valid(move_song_id):
        return HttpResponseBadRequest('Use parameters \'move_song_id\' and \'after_song_id\' to specify the track to move')
    return move_track_in_queue(move_song_id, after_song_id)

def delete_song(request):
    song_id = request.GET.get('song_id')
    if not is_string_valid(song_id):
        return HttpResponseBadRequest('Use parameter \'song_id\' to specify the song_id to delete')
    return delete_track_in_queue(song_id)

def get_queue(request):
    session_id = request.GET.get('session_id')
    if not is_string_valid(session_id):
        return HttpResponseBadRequest('Use paramter \'session_id\' to specify session_id for the queue')
    tracks = get_tracks_in_queue(session_id)
    return HttpResponse(json.dumps(tracks), content_type='application/json')
