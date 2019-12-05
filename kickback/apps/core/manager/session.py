import random
import string
import json
from kickback.apps.core.models import Sessions, CurrentSongs, SessionSongs
from kickback.apps.core.manager.chat import add_to_chat_for_session
from kickback.apps.core.manager.sockets import call_socket_for_update_queue, call_socket_for_update_followers
from kickback.apps.core.manager.user import get_following_helper
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

def is_session_id_valid(session_id):
    session_id_query = Sessions.objects.raw('SELECT * FROM core_sessions WHERE session_id = %s', [session_id])
    return (len(session_id_query) == 0)

def is_owner_valid(owner):
    owner_query = Sessions.objects.raw('SELECT * FROM core_sessions WHERE owner = %s', [owner])
    return (len(owner_query) == 0)

def random_string(length=4):
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def build_random_session_id():
    session_id = random_string()
    while not is_session_id_valid(session_id):
        session_id = random_string()
    return session_id

def build_session_name(session_id):
    return 'Kickback Session ' + str(session_id)

def create_new_session_chat_message(owner, session_id, session_name):
    return str(owner) + ' started a new session \"' + str(session_name) + '\" with Session ID \"' + str(session_id) + '\".'

def trigger_create_session_message_to_chat(owner, session_id, session_name):
    message = create_new_session_chat_message(owner, session_id, session_name)
    add_to_chat_for_session(session_id, message, 'Kickback')

@transaction.atomic
def create_session_in_db(session_id, session_name, owner, session_password):
    if not is_owner_valid(owner):
        return HttpResponseBadRequest('User has already started another session. End the existing session to create a new one.')
    if not is_session_id_valid(session_id):
        return HttpResponseBadRequest('Session ID is already taken. Enter another session_id or none to choose a random session_id.')
    if session_id is None or session_id == '':
        session_id = build_random_session_id()
    if session_name is None or session_name == '':
        session_name = build_session_name(session_id)

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO core_sessions(session_id, session_name, owner, session_password) VALUES (%s, %s, %s, %s)',
            [session_id, session_name, owner, session_password])

    call_socket_for_update_followers(get_following_helper(owner))

    trigger_create_session_message_to_chat(owner, session_id, session_name)

    session_info = {}
    session_info['session_id'] = session_id
    session_info['session_name'] = session_name
    return HttpResponse(json.dumps(session_info), content_type='application/json')

def validate_session_in_db(session_id, session_password):
    session_query = Sessions.objects.raw('SELECT * FROM core_sessions WHERE session_id=%s', [session_id])
    if len(session_query) == 1 and ((session_query[0].session_password is None) or (session_query[0].session_password == session_password)):
        session_info = {}
        session_info['session_id'] = session_id
        session_info['session_name'] = session_query[0].session_name
        return HttpResponse(json.dumps(session_info), content_type='application/json')
    return HttpResponseBadRequest('The session is not valid.')

@transaction.atomic
def end_session_in_db(session_id):
    session_query = Sessions.objects.raw('SELECT * FROM core_sessions WHERE session_id=%s', [session_id])

    if len(session_query) == 0:
        return HttpResponseBadRequest('The session_id is not valid.')

    owner = session_query[0].owner

    with connection.cursor() as cursor:
        # Need to run all DELETE queries since we cannot use the ForeignKey's CASCADE when using raw SQL queries in Django
        cursor.execute('DELETE FROM core_currentsongs WHERE session_id=%s', [session_id])
        cursor.execute('DELETE FROM core_sessionsongs WHERE session_id=%s', [session_id])
        cursor.execute('DELETE FROM core_chatmessages WHERE session_id=%s', [session_id])
        cursor.execute('DELETE FROM core_sessions WHERE session_id=%s', [session_id])

    call_socket_for_update_followers(get_following_helper(owner))

    return HttpResponse('Session ' + str(session_id) + ' has ended.')

def get_owned_session_in_db(owner):
    session_info = {}
    session_query = Sessions.objects.raw('SELECT * FROM core_sessions WHERE owner=%s', [owner])
    if len(session_query) == 1:
        session_info['session_id'] = session_query[0].session_id
        session_info['session_name'] = session_query[0].session_name
    return HttpResponse(json.dumps(session_info), content_type='application/json')

def play_next_song_in_db(session_id):
    current_song_query = CurrentSongs.objects.raw('SELECT * FROM core_currentsongs WHERE session_id = %s', [session_id])
    if len(current_song_query) == 0:
        return HttpResponseBadRequest('The session_id is not valid.')
    current_song_id = current_song_query[0].song_id
    old_current_song_query = SessionSongs.objects.raw('SELECT * FROM core_sessionsongs WHERE song_id = %s', [current_song_id])
    if len(old_current_song_query) == 0:
        return HttpResponseServerError('Current Song not found.')
    new_current_song_id = old_current_song_query[0].next_song_id
    if new_current_song_id is None:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM core_currentsongs WHERE session_id=%s', [session_id])
            cursor.execute('DELETE FROM core_sessionsongs WHERE song_id=%s', [current_song_id])
        return HttpResponse('The queue for this session has ended.')
    with connection.cursor() as cursor:
        cursor.execute('UPDATE core_currentsongs SET song_id=%s WHERE session_id=%s', [new_current_song_id, session_id])
        cursor.execute('DELETE FROM core_sessionsongs WHERE song_id=%s', [current_song_id])

    call_socket_for_update_queue(session_id)
    owner = Sessions.objects.raw('SELECT * FROM core_sessions WHERE session_id=%s', [session_id])[0].owner
    call_socket_for_update_followers(get_following_helper(owner))

    return HttpResponse('Now playing song_id: ' + str(new_current_song_id))
