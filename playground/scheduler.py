# flake8: noqa
"""
For testing schedulers
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
####

from django_celery_beat.models import PeriodicTask, PeriodicTasks


PeriodicTask.objects.filter()
