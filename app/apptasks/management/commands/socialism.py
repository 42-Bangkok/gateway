from apptasks.tasks.socialisms import task_socialism
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Commence socialism in task queue"

    def handle(self, *args, **options):
        task_socialism.delay()
        self.stdout.write(self.style.SUCCESS("Socialism has begun."))
