from appcore.models.commons import BaseAutoDate, BaseUUID
from django.contrib.postgres.fields import ArrayField
from django.db import models


class IntraProfile(BaseAutoDate, BaseUUID):
    """
    Stores the intra profile of a given user.
    often used data is stored in the model itself, while the rest is stored in HistIntraProfileData
    login: the login of the user
    intra_id: the intra ID of the user
    isBookmarked: whether the user is bookmarked by the staff
    pool_month: the month the user joined the pool
    pool_year: the year the user joined the pool
    cursus_ids: the cursus IDs the user is in
    """

    login = models.CharField(max_length=255, unique=True)
    intra_id = models.IntegerField(unique=True)
    isBookmarked = models.BooleanField(default=False)
    pool_month = models.CharField(max_length=100, null=True, blank=True)
    pool_year = models.CharField(max_length=100, null=True, blank=True)
    cursus_ids = ArrayField(models.IntegerField(), default=list)

    def __str__(self):
        return self.login


class HistIntraProfileData(BaseAutoDate, BaseUUID):
    """
    Stores historical data for a given intra profile, in JSON format.
    data: exact data returned from the intra API
    Note:
        while convienient, JSONField is slow.
        use HistIntraProfileData.objects.filter(profile=profile).order_by('-created').first() to get the latest data
    """

    profile = models.ForeignKey(
        IntraProfile,
        on_delete=models.CASCADE,
    )
    data = models.JSONField()

    def __str__(self):
        return f"{self.profile} - {self.created}"
