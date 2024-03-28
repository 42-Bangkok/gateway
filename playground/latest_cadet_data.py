# flake8: noqa
"""
For test fetching all cadet data
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

reset_queries()
filters = {}
qs = (
    HistIntraProfileData.objects.filter(**filters)
    .order_by("profile", "-created")
    .distinct("profile")
)
v = qs.values("created")
for q in v:
    print(q)
print(qs.count())
print(len(connection.queries))
