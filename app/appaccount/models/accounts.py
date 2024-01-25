import uuid
from django.db import models

from appcore.models.commons import BaseAutoDate, BaseUUID

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Extending the default Django user model.
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)


class Profile(BaseUUID, BaseAutoDate):
    """
    Model for storing user profile
    """

    GENDER_CHOICES = {
        "m": "Male",
        "f": "Female",
        "n": "Non-binary",
        "o": "Other",
        "u": "Unspecified",
    }

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(
        max_length=255,
        default="",
    )
    last_name = models.CharField(
        max_length=255,
        default="",
    )
    gender = models.CharField(
        choices=GENDER_CHOICES,
        default="u",
    )
    dob = models.DateField(
        null=True,
        default=None,
    )
    time_of_birth = models.TimeField(
        null=True,
        default=None,
    )
    medical_condition = models.TextField(
        default="",
    )
    job_title = models.TextField(
        default="",
    )
