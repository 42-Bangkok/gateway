from appcore.models.commons import BaseAutoDate, BaseUUID
from django.db import models


class CadetMeta(BaseAutoDate, BaseUUID):
    """
    Local data about a cadet, not related to the intra profile.
    Allows staff to add data to an arbitary cadet.
    This model does not have IntraProfile FK because IntraProfile is only created for 42 Bangkok cadets
    Lazy creation of this model is done on API Get
    login: the login of the user
    note: the note about the user
    """

    login = models.CharField(max_length=255, unique=True)
    note = models.TextField(default="")

    def __str__(self):
        return self.login
