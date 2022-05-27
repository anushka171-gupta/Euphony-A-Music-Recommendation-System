from http.client import LENGTH_REQUIRED
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Song(models.Model):
    name = models.CharField(max_length=1000, null=True, blank=True)
    user = models.ManyToManyField(User)
    artist = models.CharField(max_length=1000, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    preview_url = models.CharField(max_length=1000,null=True, blank=True)
    cover_art_url = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name