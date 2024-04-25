from celery import shared_task

from apptasks.services.update_intraprofile import (
    update_intraprofile as _update_intraprofile,
)
from apptasks.tasks.discord import send_simple_message


@shared_task
def update_intraprofile() -> bool:
    """
    Updates the intra profile of all cadets
    """
    try:
        _update_intraprofile()
    except Exception as e:
        send_simple_message(f"update_intraprofile(); Error: {e}", "dev")
        return False

    return True
