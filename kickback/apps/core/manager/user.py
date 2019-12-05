import os
import time
import json
from neo4j.v1 import GraphDatabase, basic_auth
from kickback.apps.core.models import Sessions, CurrentSongs
from kickback.apps.core.manager.helper import batch_get_track_from_uri, convert_spotify_track_to_kickback_track
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

# Graphene DB Credentials
GRAPHENEDB_URL = os.environ.get('GRAPHENEDB_BOLT_URL')
GRAPHENEDB_USER = os.environ.get('GRAPHENEDB_BOLT_USER')
GRAPHENEDB_PASSWORD = os.environ.get('GRAPHENEDB_BOLT_PASSWORD')

# Set up GrapheneDB
driver = GraphDatabase.driver(GRAPHENEDB_URL, auth=basic_auth(GRAPHENEDB_USER, GRAPHENEDB_PASSWORD))

def create_user_in_db(username, password):
    current_time = time.time()
    session = driver.session()
    timestamp = session.run("""
        MERGE (user:User {username: $username})
        ON CREATE SET user.password=$password, user.timestamp=$current_time
        RETURN user.timestamp AS timestamp
    """, username=username, password=password, current_time=current_time).single().value()
    session.close()
    if timestamp == current_time:
        return HttpResponse('New User created: ' + str(username))
    return HttpResponseBadRequest('User ' + str(username) + ' already exists.')

def delete_user_in_db(username, password):
    session = driver.session()
    deleted_user = session.run("""
        MATCH (user:User {username: $username, password: $password})
        WITH user, user.username as username
        DETACH DELETE user
        RETURN username
    """, username=username, password=password).single()
    session.close()
    if deleted_user is not None:
        return HttpResponse('User ' + str(username) + ' is deleted.')
    return HttpResponseBadRequest('User ' + str(username) + ' is not valid.')

def validate_user_in_db(username, password):
    session = driver.session()
    user = session.run("""
        MATCH (user:User {username: $username, password: $password})
        RETURN user AS user
    """, username=username, password=password).single()
    session.close()
    if user is not None:
        return HttpResponse('User ' + str(username) + ' exists.')
    return HttpResponseBadRequest('User is not valid.')

def follow_user_in_db(follower, following):
    if follower == following:
        return HttpResponseBadRequest('User cannot follow themselves.')
    session = driver.session()
    relation = session.run("""
        MATCH (a:User {username: $follower}), (b:User {username: $following})
        MERGE (a)-[r:FOLLOWS]->(b)
        RETURN r
    """, follower=follower, following=following).single()
    session.close()
    if relation is not None:
        return HttpResponse('User ' + str(follower) + ' is following ' + str(following))
    return HttpResponseBadRequest('User ' + str(follower) + ' or ' + str(following) + ' does not exist.')

def unfollow_user_in_db(follower, following):
    session = driver.session()
    session.run("""
        MATCH (a:User {username: $follower})-[r:FOLLOWS]->(b:User {username: $following})
        DELETE r
    """, follower=follower, following=following)
    session.close()
    return HttpResponse('User ' + str(follower) + ' has unfollowed ' + str(following))

def get_following_helper(username):
    session = driver.session()
    following_users_query = session.run("""
        MATCH (a:User {username: $username})-[r:FOLLOWS]->(b:User)
        RETURN b.username as username
    """, username=username)
    session.close()

    following_users = []
    for following_user in following_users_query:
        following_users.append(following_user['username'])

    return following_users

def get_following_for_user(username):
    following_users = []
    owner_followers = set()

    session = driver.session()
    following_users_query = session.run("""
        MATCH (a:User {username: $username})-[r:FOLLOWS]->(b:User)
        RETURN b.username as username
    """, username=username)
    session.close()

    following_user_list = []
    for following_user in following_users_query:
        following_user_list.append(following_user['username'])

    if len(following_user_list) == 0:
        return HttpResponse(json.dumps([]), content_type='application/json')

    sessions_query = Sessions.objects.raw("""
        SELECT s.session_id, s.session_name, s.owner, ss.spotify_uri
        FROM core_sessions s
        INNER JOIN core_currentsongs c ON s.session_id = c.session_id
        INNER JOIN core_sessionsongs ss ON c.song_id = ss.song_id
        WHERE s.owner IN %s
    """, [tuple(following_user_list)])

    spotify_uri_list = []
    for session in sessions_query:
        spotify_uri_list.append(session.spotify_uri)

    if len(spotify_uri_list) > 0:
        spotify_track_list_info = batch_get_track_from_uri(spotify_uri_list)
        track_list_info = list(map(convert_spotify_track_to_kickback_track, spotify_track_list_info['tracks']))

        spotify_uri_to_track_info = {}
        for track in track_list_info:
            spotify_uri_to_track_info[track['uri']] = track

        for session in sessions_query:
            owner_info = {}
            owner_info['session_id'] = session.session_id
            owner_info['session_name'] = session.session_name
            owner_info['now_playing'] = spotify_uri_to_track_info[session.spotify_uri]
            following_users.append({session.owner: owner_info})
            owner_followers.add(session.owner)

    for user in following_user_list:
        if user not in owner_followers:
            following_users.append({user: {}})

    return HttpResponse(json.dumps(following_users), content_type='application/json')
