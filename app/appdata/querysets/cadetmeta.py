from appdata.models.intras import HistIntraProfileData


def query_latest_hist_intra_profile_data():
    """
    Returns the latest historical intra profile data for each profile
    """
    filters = {}
    qs = (
        HistIntraProfileData.objects.filter(**filters)
        .order_by("profile", "-created")
        .distinct("profile")
    )

    return qs
