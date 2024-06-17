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
    count = 0
    try:
        _update_intraprofile()
        send_simple_message("update_intraprofle(); Bonjour", "dev")
    except Exception as e:
        send_simple_message(f"update_intraprofile(); Error: {e}", "dev")
        while count < 3:
            try:
                send_simple_message("update_intraprofle(); Retrying...", "dev")
                _update_intraprofile()
                send_simple_message("update_intraprofle(); Bonjour", "dev")
                break
            except Exception as e:
                send_simple_message(f"update_intraprofile(); Error: {e}", "dev")
                count += 1
        return False

    return True
