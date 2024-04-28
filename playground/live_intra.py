"""
For test fetching live cadet data
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from appcore.services.intra.user import IntraUser

####


u = IntraUser("id")
