import json
from kickback.apps.core.models import ChatMessages
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

@transaction.atomic
def add_to_chat_for_session(session_id, message, username):
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO core_chatmessages(session_id, message, username) VALUES (%s, %s, %s)',
            [session_id, message, username])
    return HttpResponse('Chat has been added')

def retrieve_chat_for_session(session_id):
    chat_query = ChatMessages.objects.raw('SELECT * FROM core_chatmessages WHERE session_id=%s ORDER BY message_id', [session_id])
    return HttpResponse(json.dumps(chat_query), content_type='application/json')
