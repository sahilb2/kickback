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
]
