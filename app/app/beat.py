"""
Configuration for Celery Beat Scheduler
https://docs.celeryq.dev/en/latest/userguide/periodic-tasks.html#introduction

syntax:
    'task_name': {
        'task': '{app_name}.tasks.{module}.{function}',
        'schedule': {seconds},
        'args': ({arg}),
    },

"""
from celery.schedules import crontab

beat_schedule = {
    # Add your tasks here example:
    # 'ping': {
    #     'task': 'appcore.tasks.sample.pong',
    #     'schedule': 10.0,
    #     'args': (),
    # }
    "socialism": {
        "task": "appcommons.tasks.communism.task_socialism",
        "schedule": crontab(hour=7, minute=42, day_of_week=1),
        "args": (),
    },
}
