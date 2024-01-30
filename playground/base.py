# flake8: noqa
"""
For testing user creation
"""
import os

import django
from appcore.services.utils import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
####
