from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
import json
from kickback.apps.core.manager.search import search_tracks_by_query
from kickback.apps.core.manager.getQueue import get_tracks_in_queue

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
    return HttpResponse('Add Song Endpoint')

def move_song(request):
    sessionId = request.POST.get('sessionId')
    moveSong = request.POST.get('moveSongId')
    afterSong = request.POST.get('afterSongId')
    if (sessionId is None or moveSong is None or afterSong is None):
        return HttpResponseBadRequest('Use parameters \'sessionId\', \'moveSongId\', and \'afterSongId\' to specify what to move')
    return HttpResponse('Song Moved')

def delete_song(request):
    return HttpResponse('Delete Song Endpoint')

def get_queue(request):
    sessionId = request.GET.get('q')
    if sessionId is None or sessionId == '':
        return HttpResponseBadRequest('Use parameter \'q\' to specify sessionId for the queue')
    tracks = get_tracks_in_queue(sessionId)
    return HttpResponse(json.dumps(tracks), content_type='application/json')
