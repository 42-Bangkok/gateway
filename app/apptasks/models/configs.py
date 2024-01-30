from appcore.models.commons import BaseAutoDate, BaseUUID
from django.db import models


class DiscordWebhook(BaseAutoDate, BaseUUID):
    """
    Represents a Discord webhook.
    """

    name = models.CharField(unique=True)
    url = models.URLField()

    def __str__(self):
        return self.name
