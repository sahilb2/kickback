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
    messages_query = ChatMessages.objects.raw('SELECT * FROM core_chatmessages WHERE session_id=%s ORDER BY message_id', [session_id])

    total_messages_query = ChatMessages.objects.raw("""
        SELECT username, COUNT(*) as user_message_count
        FROM core_chatmessages
        GROUP BY username, session_id
        HAVING session_id=%s
        ORDER BY user_message_count DESC
    """, [session_id])

    user_total_messages = []
    for row in total_messages_query:
        user_total_messages.append({row.username: row.user_message_count})

    messages = []
    for message in messages_query:
        message_info = {}
        message_info['message_id'] = message.message_id
        message_info['message'] = message.message
        message_info['username'] = message.username
        messages.append(message_info)

    chat = {}
    chat['messages'] = messages
    chat['user_total_messages'] = user_total_messages
    return HttpResponse(json.dumps(chat), content_type='application/json')
