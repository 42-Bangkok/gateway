from apptasks.services.update_intraprofile import update_intraprofile
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Manually update intra profile of all cadets."

    def handle(self, *args, **options):
        update_intraprofile()
