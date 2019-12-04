import random
import string
from kickback.apps.core.models import Sessions
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

@transaction.atomic
def create_session_in_db(session_id, session_name, owner, session_password):
    if session_id is None:
        session_id = build_random_session_id()
    if session_name is None:
        session_name = build_session_name(session_id)

    # Make sure only uppercase letters are stored in the database to make session_id case insensitive
    session_id = session_id.upper()

    if not is_session_id_valid(session_id):
        return HttpResponseBadRequest('Session ID is already taken. Enter another session_id or none to choose a random session_id.')
    if not is_owner_valid(owner):
        return HttpResponseBadRequest('User has already started another session. End the existing session to create a new one.')

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO core_sessions(session_id, session_name, owner, session_password) VALUES (%s, %s, %s, %s)',
            [session_id, session_name, owner, session_password])

    return HttpResponse('Session created with session_id: ' + str(session_id))
