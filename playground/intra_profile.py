# flake8: noqa
"""
For test resolving cadet data
"""
import os

import django
from appcore.services.utils import slugify
from django.db.models import OuterRef, Subquery, Prefetch, Max

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
####
from rich import inspect
from appdata.models.intras import IntraProfile, HistIntraProfileData
from django.db import connection, reset_queries

from dateutil.parser import isoparse
from django.utils import timezone

data = (
    HistIntraProfileData.objects.filter(profile__login="krchuaip")
    .order_by("-created")
    .first()
    .data
)

for c in data["cursus_users"]:
    print(c["cursus"]["name"])
    print(c["blackholed_at"])

timezone.now() > isoparse("2022-09-29T06:42:00.000Z")
