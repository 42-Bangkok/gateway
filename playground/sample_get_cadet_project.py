# flake8: noqa
"""
query users by project and status
"""
import os
import time
import django
from rich import print


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
####

from appdata.models.intras import HistIntraProfileData
from django.db.models import OuterRef, Subquery
from django.db import connection, reset_queries

reset_queries()

# can be optimized by storing latest project info in the profile model itself
latest_data_subquery = (
    HistIntraProfileData.objects.filter(
        data__icontains="ft_transcendence",
        profile=OuterRef("profile"),
    )
    .order_by("-created")
    .values("id")[:1]
)

latest_data = HistIntraProfileData.objects.filter(
    id=Subquery(latest_data_subquery)
).all()

# Look for cadets attempting transcendence
# latest_data.count()
count = 0
start = time.time()
for i in latest_data:
    for project_user in i.data["projects_users"]:
        if (
            project_user["project"]["id"] == 1337
            and project_user["status"] != "finished"
            # and project_user["final_mark"] is not None
            # and project_user["final_mark"] >= 100
        ):
            # print(project_user)
            print(f'{i.data["login"]}: {i.data["first_name"]} {i.data["last_name"]}')
            count += 1
print(f"{count=}")
print(f"{time.time() - start:.2f}s")

print(len(connection.queries))
print(connection.queries)
