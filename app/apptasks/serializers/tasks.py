import json
from ninja import Field, ModelSchema, Schema
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from pydantic import field_validator


class PeriodicTaskSchema(ModelSchema):
    class Meta:
        model = PeriodicTask
        fields = ["id", "name", "enabled"]


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


class CronScheduleSchema(ModelSchema):
    timezone: str = "Asia/Bangkok"

    class Meta:
        model = CrontabSchedule
        exclude = ["id"]


class CreateSnappyKwargs(Schema):
    cursus_id: int
    sheet_name_static: str
    sheet_name: str
    pool_month: str | None = Field(None, examples=["january", "february", "march"])
    pool_year: int | None = None
    only_id_after: int | None = None
    skip_logins: list[str] | None = None


class CreateSnappyTaskPostIn(Schema):
    name: str = Field(..., examples=["snappy.snap-discovery"])
    cron_schedule: CronScheduleSchema
    kwargs: CreateSnappyKwargs

    @field_validator("name")
    def name_must_be_unique(cls, v):
        if PeriodicTask.objects.filter(name=v).exists():
            raise ValueError("name must be unique")
        return v

    @field_validator("name")
    def name_must_begin_with_snappy(cls, v):
        if not v.startswith("snappy."):
            raise ValueError("name must begin with snappy.")
        return v


class SnappyTaskPatchIn(Schema):
    name: str = Field(None, examples=["snappy.snap-discovery"])
    enabled: bool = None
    cron_schedule: CronScheduleSchema
    kwargs: CreateSnappyKwargs = None

    @field_validator("name")
    def name_must_be_unique(cls, v):
        if PeriodicTask.objects.filter(name=v).exists():
            raise ValueError("name must be unique")
        return v

    @field_validator("name")
    def name_must_begin_with_snappy(cls, v):
        if not v.startswith("snappy."):
            raise ValueError("name must begin with snappy.")
        return v
