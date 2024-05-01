import json
from ninja import Router
from django_celery_beat.models import PeriodicTask, CrontabSchedule


from appcore.serializers.commons import ErrorResponse
from apptasks.serializers.tasks import (
    CreateSnappyTaskPostIn,
    SnappyTaskPatchIn,
    TaskGetOut,
    TasksGetOut,
)

router = Router(tags=["tasks"])


@router.get(
    "/",
    response={200: TasksGetOut},
)
def get_tasks(request, startswith: str = None):
    """
    Get all tasks
    Query Parameters:
    - name_contains: str (optional) - Filter tasks by name
    """

    tasks = PeriodicTask.objects.filter()
    if startswith:
        tasks = tasks.filter(name__istartswith=startswith)

    return {"items": tasks}


@router.post(
    "/snappy/",
    response={200: None},
)
def post_snappy_task(request, payload: CreateSnappyTaskPostIn):
    """
    Create a new snappy to gsheet task
    """

    schedule, _ = CrontabSchedule.objects.get_or_create(
        **payload.cron_schedule.model_dump()
    )
    PeriodicTask.objects.create(
        crontab=schedule,
        name=payload.name,
        task="apptasks.tasks.snappy.snap_to_gsheet",
        kwargs=json.dumps(payload.kwargs.model_dump()),
    )
    return 200, None


@router.patch(
    "/snappy/{id}/",
    response={
        200: None,
        400: ErrorResponse,
        404: None,
    },
)
def patch_snappy_task(request, id: int, payload: SnappyTaskPatchIn):
    """
    Patch a snappy task
    """
    task = PeriodicTask.objects.filter(id=id).first()
    if task is None:
        return 404, None
    for key, value in payload.model_dump(exclude_unset=True).items():
        match key:
            case "kwargs":
                setattr(task, key, json.dumps(value))
            case "cron_schedule":
                schedule, _ = CrontabSchedule.objects.get_or_create(
                    **value.model_dump()
                )
                setattr(task, "crontab", schedule)
            case _:
                setattr(task, key, value)
    task.save()
    return None


@router.get(
    "/{id}/",
    response={200: TaskGetOut, 404: None},
)
def get_task(request, id: int):
    """
    Get a task
    Path Parameters:
    - id: int - Task ID
    """

    task = PeriodicTask.objects.filter(id=id).first()
    if task is None:
        return 404, None

    return task
