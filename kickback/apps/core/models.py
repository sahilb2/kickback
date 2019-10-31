from django.db import models

class User(models.Model):
    user_id = models.AutoField(auto_created=True, primary_key=True, verbose_name='User ID')
    username = models.CharField(max_length=255, blank=False)

class Sessions(models.Model):
    session_id = models.CharField(max_length=6, primary_key=True, verbose_name='Session ID')
    session_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='Session Name')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True, verbose_name='Session Owner')

class SessionSongs(models.Model):
    song_id = models.AutoField(auto_created=True, primary_key=True, verbose_name='Song ID')
    session_id = models.ForeignKey(Sessions, on_delete=models.CASCADE, verbose_name='Session ID')
    spotify_uri = models.CharField(max_length=22, blank=False, verbose_name='Song URI')
    next_song_id = models.IntegerField(blank=True, null=True, verbose_name='Next Song ID')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False, verbose_name='Added By User')
