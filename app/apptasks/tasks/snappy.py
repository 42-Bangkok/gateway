import logging
import threading
from time import sleep

import pandas as pd
from celery import shared_task
from pydantic import validate_call

from appcore.services.intra.intra import Intra
from appcore.services.intra.user import IntraUser
from appdata.models.intras import IntraProfile
from apptasks.tasks.utils import human_time, upload2gsheet, upload2gsheet_static

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@shared_task
@validate_call
def snap_to_gsheet(
    cursus_id: int,
    sheet_name_static: str,
    sheet_name: str,
    pool_month: str | None = None,
    pool_year: int | None = None,
    only_id_after: int | None = None,
    skip_logins: list[str] | None = None,
) -> bool:
    """
    Snapshots the data of all cadets in a given cursus to a Google Sheet.
    With calculated data such as:
    - Inactive for
    - Level
    - Correction point
    - As evaluator
    - As evaluated
    - Total tries
    - Project score
    ... and more
    """
    api = Intra()

    # Get cadets
    logger.info("Getting cadets...")
    intra_profiles = IntraProfile.objects.filter(
        cursus_ids__contains=[cursus_id],
    )
    if pool_month:
        intra_profiles = intra_profiles.filter(pool_month=pool_month)
    if pool_year:
        intra_profiles = intra_profiles.filter(pool_year=pool_year)
    if skip_logins:
        intra_profiles = intra_profiles.exclude(login__in=skip_logins)
    if only_id_after:
        intra_profiles = intra_profiles.exclude(intra_id__gte=only_id_after)
    intra_users = [
        IntraUser(profile.login, profile.histintraprofiledata_set.last().data)
        for profile in intra_profiles
    ]

    # Hydrate pts_gain and pts_lost for each intra user
    logger.info("Hydrating pts_gain and pts_lost for each intra user...")

    def _hydrate_pts_gain_loss(user):
        user.calc_eval_pts_gainloss()

    thrs = []
    for user in intra_users:
        thr = threading.Thread(target=_hydrate_pts_gain_loss, args=(user,))
        thrs.append(thr)

    for thr in thrs:
        thr.start()
        sleep(0.5)  # prevents rate limit

    for thr in thrs:
        thr.join()

    # Get project slugs
    logger.info("Getting project slugs...")
    projects = api.get_projects_by_cursus(cursus_id)
    slugs = []
    for p in projects:
        slugs.append(p["slug"])

    # prep df payload
    df_data = []
    for user in intra_users:
        d = {
            "email": user.data["email"],
            "login": user.data["login"],
            "id": user.data["id"],
            "first_name": user.data["first_name"],
            "last_name": user.data["last_name"],
            "profile_url": f'https://profile.intra.42.fr/users/{user.data["login"]}',
            "inactive_for": user.get_days_since_last_active_date_by_project_update(
                cursus_id=cursus_id
            ),
            "level": user.level(cursus_id=cursus_id),
            "correction_point": user.data["correction_point"],
            "as_evaluator": user.pts_gain,
            "as_evaluated": user.pts_lost,
            "total_tries": user.calc_total_tries(cursus_id=cursus_id),
        }
        # project score, completed date
        for s in slugs:
            d[s] = user.project_final_mark(cursus_id=cursus_id, project_slug=s)
            d_project = user.project(cursus_id=cursus_id, project_slug=s)
            # get project status
            d[f"{s}_status"] = d_project.get("status", None)
            d[f"{s}_updated_at"] = d_project.get("updated_at", None)
        df_data.append(d)
    df = pd.DataFrame(df_data)

    # upload payload to gsheet
    upload2gsheet_static(
        df,
        sheet_name_static,
        oauth=False,
        service_account_file="service_account.json",
    )
    upload2gsheet(
        df,
        sheet_name,
        human_time(),
        oauth=False,
        service_account_file="service_account.json",
    )
    return True
