from django.urls import path, re_path

from django.contrib import admin

admin.autodiscover()

import kickback.apps.core.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", kickback.apps.core.views.index, name="index"),

    re_path(r'^search/$', kickback.apps.core.views.search, name="search"),

    re_path(r'^add_song/$', kickback.apps.core.views.add_song, name="add_song"),
    re_path(r'^move_song/$', kickback.apps.core.views.move_song, name="move_song"),
    re_path(r'^delete_song/$', kickback.apps.core.views.delete_song, name="delete_song"),
    re_path(r'^get_queue/$', kickback.apps.core.views.get_queue, name="get_queue"),

    re_path(r'^create_user/$', kickback.apps.core.views.create_user, name="create_user"),
    re_path(r'^delete_user/$', kickback.apps.core.views.delete_user, name="delete_user"),
    re_path(r'^validate_user/$', kickback.apps.core.views.validate_user, name="validate_user"),
    re_path(r'^follow_user/$', kickback.apps.core.views.follow_user, name="follow_user"),
    re_path(r'^unfollow_user/$', kickback.apps.core.views.unfollow_user, name="unfollow_user"),
    re_path(r'^get_following/$', kickback.apps.core.views.get_following, name="get_following"),

    re_path(r'^create_session/$', kickback.apps.core.views.create_session, name="create_session"),
    re_path(r'^validate_session/$', kickback.apps.core.views.validate_session, name="validate_session"),
    re_path(r'^end_session/$', kickback.apps.core.views.end_session, name="end_session"),
    re_path(r'^get_owned_session/$', kickback.apps.core.views.get_owned_session, name="get_owned_session"),
    re_path(r'^play_next_song/$', kickback.apps.core.views.play_next_song, name="play_next_song"),
]
