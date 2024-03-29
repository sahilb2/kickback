import json
from kickback.apps.core.models import ChatMessages
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from kickback.apps.core.manager.sockets import call_socket_for_update_chat

@transaction.atomic
def add_to_chat_for_session(session_id, message, username):
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO core_chatmessages(session_id, message, username) VALUES (%s, %s, %s)',
            [session_id, message, username])
    call_socket_for_update_chat(session_id)
    return HttpResponse('Chat has been added')

def retrieve_chat_for_session(session_id):
    chat_query = ChatMessages.objects.raw('SELECT * FROM core_chatmessages WHERE session_id=%s ORDER BY message_id', [session_id])
    chats = []
    for chat in chat_query:
        message = {}
        message['username'] = chat.username
        message['message'] = chat.message
        chats.append(message)
    return HttpResponse(json.dumps(chats), content_type='application/json')
