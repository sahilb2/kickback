import os
import time
from neo4j.v1 import GraphDatabase, basic_auth
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
