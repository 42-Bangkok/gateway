import json
from ninja import Router
from django_celery_beat.models import PeriodicTask

from apptasks.serializers.snappy import (
    TaskGetOut,
    TaskPatchIn,
    TaskPatchOut,
    TasksGetOut,
)

router = Router(tags=["tasks"])


@router.get(
    "/",
    response={200: TasksGetOut},
)
def get_tasks(request, name_contains: str = None):
    """
    Get all tasks
    Query Parameters:
    - name_contains: str (optional) - Filter tasks by name
    """

    tasks = PeriodicTask.objects.filter()
    if name_contains:
        tasks = tasks.filter(name__icontains=name_contains)

    return {"items": tasks}


@router.get(
    "/{id}/",
    response={200: TaskGetOut},
)
def get_task(request, id: int):
    """
    Get a task
    Path Parameters:
    - id: int - Task ID
    """

    task = PeriodicTask.objects.get(id=id)

    return task


@router.patch(
    "/{id}/",
    response={200: TaskPatchOut, 404: None},
)
def patch_task(request, payload: TaskPatchIn, id: int):
    """
    Patch a task
    Path Parameters:
    - id: int - Task ID
    Payload:
    - enabled: bool (optional) - Task enabled status
    - kwargs: dict (optional) - Task kwargs
    """

    task = PeriodicTask.objects.filter(id=id).first()
    if task is None:
        return 404, None
    for key, value in payload.model_dump(exclude_unset=True).items():
        match key:
            case "kwargs":
                setattr(task, key, json.dumps(value))
            case _:
                setattr(task, key, value)
    task.save()

    return task
