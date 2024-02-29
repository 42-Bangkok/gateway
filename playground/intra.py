# flake8: noqa
"""
Dumps all project slugs to a file
"""
import json
import os

import django
from appcore.services.utils import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
####
from appcore.services.intra.intra import Intra as Api


api = Api()
projects = api.get_projects_by_cursus(69)
slugs = []
for p in projects:
    slugs.append(p["slug"])
with open("slugs.txt", "w") as f:
    json.dump(slugs, f)
