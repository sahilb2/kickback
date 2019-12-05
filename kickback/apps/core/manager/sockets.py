import requests

def call_socket_for_update_chat(session_id):
    requests.post('https://kickback-socket-server.herokuapp.com/updateChat', {'sessionid': session_id})

def call_socket_for_update_queue(session_id):
    requests.post('https://kickback-socket-server.herokuapp.com/updateQueue', {'sessionid': session_id})

def call_socket_for_update_followers(usernames):
    requests.post('https://kickback-socket-server.herokuapp.com/updateFollowers', {'usernames': usernames})
