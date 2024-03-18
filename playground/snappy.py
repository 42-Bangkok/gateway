# flake8: noqa
"""
For testing snappy creation
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
####


from apptasks.tasks.snappy import snap_to_gsheet
from celery.result import AsyncResult

cursus_id = 69
skip_logins = ["armel"]
only_id_after = 1000000
pool_month = "january"
pool_year = 2022
sheet_name_static = "test_snappy_static"
sheet_name = "test_snappy"

res = snap_to_gsheet.delay(
    cursus_id=cursus_id,
    sheet_name_static=sheet_name_static,
    sheet_name=sheet_name,
    pool_month=pool_month,
    pool_year=pool_year,
    only_id_after=only_id_after,
    skip_logins=skip_logins,
)
