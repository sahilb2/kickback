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
]
