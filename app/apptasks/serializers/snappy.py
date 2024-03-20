import json
from ninja import ModelSchema, Schema
from django_celery_beat.models import PeriodicTask


class PeriodicTaskSchema(ModelSchema):
    class Meta:
        model = PeriodicTask
        fields = ["id", "name"]


class TasksGetOut(Schema):
    items: list[PeriodicTaskSchema]


class TaskGetOut(ModelSchema):
    kwargs: dict

    class Meta:
        model = PeriodicTask
        fields = "__all__"

    @staticmethod
    def resolve_kwargs(obj):
        return json.loads(obj.kwargs)


class TaskPatchIn(Schema):
    enabled: bool = None
    kwargs: dict = None


class TaskPatchOut(TaskGetOut): ...
