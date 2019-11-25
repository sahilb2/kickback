from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.http import require_http_methods
from django.db import transaction, connection
import json
from kickback.apps.core.manager.helper import is_string_valid, test_graphene_db
from kickback.apps.core.manager.search import search_tracks_by_query
from kickback.apps.core.manager.get_queue import get_tracks_in_queue
from kickback.apps.core.manager.add_song import add_track_in_queue
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

def add_song(request):
    session_id = request.GET.get('session_id')
    spotify_uri = request.GET.get('uri')
    user_id = request.GET.get('user_id')
    if not (is_string_valid(session_id) and is_string_valid(spotify_uri) and is_string_valid(user_id)):
        return HttpResponseBadRequest('Use paramter \'session_id\' to specify session_id,' +
         '\'uri\' to specify the Spotify URI of the track, and \'user_id\' to specify username of the user who added the song')
    return add_track_in_queue(session_id, spotify_uri, user_id)

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

def test(request):
    return HttpResponse(json.dumps(test_graphene_db()), content_type='application/json')
