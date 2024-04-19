"""
Aggregates intra data
"""

from typing import Literal
from django.utils import timezone
from dateutil.parser import isoparse
from ninja import Router

from appdata.models.intras import HistIntraProfileData
from appdata.serializers.intra import CadetStatusGetOut

router = Router(tags=["intra-data"])


@router.get(
    "user/{login}/status/",
    response={200: CadetStatusGetOut, 404: None},
)
def get_cadet_status(request, login: str):
    """
    Resolves the cadet status of the given login for the pedago usage\n
    ```
    blackholed: true if blackholed in 42cursus, false otherwise
    enrollment: cadet | pisciner | no-cursus
    ```
    """

    def _is_blackholed(data) -> bool:
        """
        Checks if the cadet's 42cursus is blackholed
        Args:
            data: The intra profile data
        Returns:
            bool: True if blackholed in 42cursus, False otherwise
        """
        for cursus in data["cursus_users"]:
            if cursus["cursus"]["slug"] == "42cursus":
                if cursus["blackholed_at"] is None:
                    return False
                return timezone.now() > isoparse(cursus["blackholed_at"])

        return False

    def _resolve_enrollment(data) -> Literal["cadet", "pisciner", "no-cursus"]:
        """
        Resolves the enrollment status of the cadet
        Args:
            data: The intra profile data
        Returns:
            str: The enrollment status of the cadet
        """
        if len(data["cursus_users"]) == 0:
            return "no-cursus"

        for cursus in data["cursus_users"]:
            if cursus["cursus"]["slug"] == "42cursus":
                return "cadet"

        return "pisciner"

    q = (
        HistIntraProfileData.objects.filter(profile__login=login)
        .order_by("-created")
        .first()
    )

    if q is None:
        return 404, None

    data = q.data

    ret = {
        "updated": q.created,
        "blackholed": _is_blackholed(data),
        "enrollment": _resolve_enrollment(data),
    }

    return 200, ret
