from celery import shared_task

from apptasks.services.update_intraprofile import (
    update_intraprofile as _update_intraprofile,
)


@shared_task
def update_intraprofile() -> bool:
    """
    Updates the intra profile of all cadets
    """
    return _update_intraprofile()
