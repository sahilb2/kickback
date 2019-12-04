from django.db import models

class Sessions(models.Model):
    session_id = models.CharField(max_length=4, primary_key=True, verbose_name='Session ID')
    session_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='Session Name')
    owner = models.CharField(max_length=20, blank=False, null=True, verbose_name='Session Owner')
    session_pass = models.CharField(max_length=16, blank=True, null=True, verbose_name='Session Password')

class SessionSongs(models.Model):
    song_id = models.AutoField(auto_created=True, primary_key=True, verbose_name='Song ID')
    spotify_uri = models.CharField(max_length=22, blank=False, verbose_name='Song URI')
    next_song_id = models.IntegerField(blank=True, null=True, verbose_name='Next Song ID')
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, verbose_name='Session ID')
    username = models.CharField(max_length=20, blank=False, null=True, verbose_name='Added By User')

class CurrentSongs(models.Model):
    session = models.OneToOneField(Sessions, on_delete=models.CASCADE, verbose_name='Session ID')
    song = models.ForeignKey(SessionSongs, on_delete=models.PROTECT, verbose_name='Song ID')
