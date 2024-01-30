from apptasks.services.socialisms import socialism
from celery import shared_task


@shared_task
def task_socialism() -> bool:
    """
    Socialism takes away points from students who have more than 10 points and add to the pool
    """
    return socialism(target=10, dry_run=False)
