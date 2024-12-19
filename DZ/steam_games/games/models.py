from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=255)
    app_id = models.IntegerField(unique=True)
    playtime_forever = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Profile(models.Model):
    steam_id = models.CharField(max_length=50, unique=True)
    avatar_url = models.URLField(blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nickname} ({self.steam_id})"
