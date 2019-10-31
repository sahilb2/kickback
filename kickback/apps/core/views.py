from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
import json
from kickback.apps.core.manager.search import search_tracks_by_query

from .models import User, Sessions, SessionSongs

def index(request):
    return HttpResponse('Team Frabric presents Kickback Backend!')

def search(request):
    query = request.GET.get('q')
    if query is None or query == '':
        return HttpResponseBadRequest('Use paramter \'q\' to specify query for the search')
    tracks = search_tracks_by_query(query)
    return HttpResponse(json.dumps(tracks), content_type='application/json')

def add_song(request):
    return HttpResponse('Add Song Endpoint')

def move_song(request):
    return HttpResponse('Move Song Endpoint')

def delete_song(request):
    return HttpResponse('Delete Song Endpoint')

def get_queue(request):
    return HttpResponse('Get Queue Endpoint')
