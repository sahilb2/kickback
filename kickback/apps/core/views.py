from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.http import require_http_methods
from django.db import transaction, connection
import json
from kickback.apps.core.manager.helper import is_string_valid
from kickback.apps.core.manager.search import search_tracks_by_query
from kickback.apps.core.manager.get_queue import get_tracks_in_queue
from kickback.apps.core.manager.add_song import add_track_in_queue
from kickback.apps.core.manager.move_song import move_track_in_queue
from kickback.apps.core.manager.delete_song import delete_track_in_queue
from kickback.apps.core.manager.user import create_user_in_db, delete_user_in_db, validate_user_in_db, follow_user_in_db, unfollow_user_in_db
from kickback.apps.core.manager.session import create_session_in_db, validate_session_in_db, end_session_in_db

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
    username = request.GET.get('username')
    if not (is_string_valid(session_id) and is_string_valid(spotify_uri) and is_string_valid(username)):
        return HttpResponseBadRequest('Use paramter \'session_id\' to specify session_id,' +
         '\'uri\' to specify the Spotify URI of the track, and \'username\' to specify username of the user who added the song')
    return add_track_in_queue(session_id, spotify_uri, username)

def move_song(request):
    move_song_id = request.GET.get('move_song_id')
    after_song_id = request.GET.get('after_song_id')
    session_id = request.GET.get('session_id')
    if not (is_string_valid(move_song_id) and is_string_valid(session_id)):
        return HttpResponseBadRequest('Use parameters \'session_id\', \'move_song_id\', and \'after_song_id\' to specify the track to move')
    return move_track_in_queue(session_id, move_song_id, after_song_id)

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

def create_user(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    if not (is_string_valid(username) and is_string_valid(password)):
        return HttpResponseBadRequest('Use parameters \'username\' and \'password\' to create a user')
    return create_user_in_db(username, password)

def delete_user(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    if not (is_string_valid(username) and is_string_valid(password)):
        return HttpResponseBadRequest('Use parameters \'username\' and \'password\' to delete a user')
    return delete_user_in_db(username, password)

def validate_user(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    if not (is_string_valid(username) and is_string_valid(password)):
        return HttpResponseBadRequest('Use parameters \'username\' and \'password\' to validate a user')
    return validate_user_in_db(username, password)

def follow_user(request):
    follower = request.GET.get('follower')
    following = request.GET.get('following')
    if not (is_string_valid(follower) and is_string_valid(following)):
        return HttpResponseBadRequest('Use parameters \'follower\' and \'following\' to follow a user')
    return follow_user_in_db(follower, following)

def unfollow_user(request):
    follower = request.GET.get('follower')
    following = request.GET.get('following')
    if not (is_string_valid(follower) and is_string_valid(following)):
        return HttpResponseBadRequest('Use parameters \'follower\' and \'following\' to unfollow a user')
    return unfollow_user_in_db(follower, following)

def create_session(request):
    session_id = request.GET.get('session_id')
    session_name = request.GET.get('session_name')
    owner = request.GET.get('owner')
    session_password = request.GET.get('session_password')
    if not is_string_valid(owner):
        return HttpResponseBadRequest('Use parameters \'session_id\', \'session_name\', \'owner\' (required), and \'session_password\' to create a session')
    return create_session_in_db(session_id, session_name, owner, session_password)

def validate_session(request):
    session_id = request.GET.get('session_id')
    session_password = request.GET.get('session_password')
    if not is_string_valid(session_id):
        return HttpResponseBadRequest('Use parameters \'session_id\' (required) and \'session_password\' to validate a session')
    return validate_session_in_db(session_id, session_password)

def end_session(request):
    session_id = request.GET.get('session_id')
    if not is_string_valid(session_id):
        return HttpResponseBadRequest('Use parameters \'session_id\' (required) to end a session')
    return end_session_in_db(session_id)
