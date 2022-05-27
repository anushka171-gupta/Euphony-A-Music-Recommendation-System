from django.urls import path, include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("explore/", views.explore, name="explore"),
    path("playlist/", views.playlist, name="playlist"),
    path("artist/<id>", views.artist, name="artist"),
    path("song/<id>", views.song, name="song"),
    path("remove", views.delete, name="delete")
]


urlpatterns += staticfiles_urlpatterns()