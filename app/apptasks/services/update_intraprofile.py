from datetime import datetime

from appcore.services.date_utils import month_range_from_now
from appcore.services.intra.intra import Intra
from appcore.services.console import console
from appdata.models.intras import HistIntraProfileData, IntraProfile


def update_intraprofile() -> bool:
    """
    Updates the intra profile of all cadets
    Returns:
        True if successful
    cursus id 75 Pro training - AI
    cursus id 74 Pro training - Cybersecurity
    cursus id 21 Main cursus
    cursus id 9 C Piscine
    cursus id 3 Discovery
    cursus id 69 Python
    """
    CURSUS_IDS = [9, 3, 21, 74, 75, 69]
    FILTER = {
        "filter[primary_campus_id]": 33,
    }

    intra = Intra()
    curr_year = datetime.now().year
    logins = []
    for cursus_id in CURSUS_IDS:
        users = intra.get_users_by_cursus_id(cursus_id, filter=FILTER)
        if cursus_id == 9 or cursus_id == 3:
            for user in users:
                if user["pool_year"] is None or user["pool_month"] is None:
                    continue
                if int(user["pool_year"]) == curr_year and user[
                    "pool_month"
                ] in month_range_from_now(2):
                    logins.append(user["login"])
        else:
            logins += [i["login"] for i in users]
    logins = list(set(logins))
    console.log(f"Logins to fetch: {len(logins)}")
    user_infos = intra.get_user_infos_thr(logins)
    hist_intra_profile_data_s = []
    for user_info in user_infos:
        intra_profile, _ = IntraProfile.objects.get_or_create(
            intra_id=user_info["id"],
        )
        if intra_profile.login != user_info["login"]:
            intra_profile.login = user_info["login"]
        intra_profile.pool_month = user_info["pool_month"]
        intra_profile.pool_year = user_info["pool_year"]
        intra_profile.cursus_ids = [
            cursus["cursus_id"] for cursus in user_info["cursus_users"]
        ]
        intra_profile.save()
        hist_intra_profile_data_s.append(
            HistIntraProfileData(
                profile=intra_profile,
                data=user_info,
            )
        )
    HistIntraProfileData.objects.bulk_create(
        hist_intra_profile_data_s, ignore_conflicts=True
    )

    return True
