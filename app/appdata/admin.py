from django.contrib import admin

from appdata.models.cadetmetas import CadetMeta
from appdata.models.intras import IntraProfile


# Register your models here.
admin.site.register(CadetMeta)
admin.site.register(IntraProfile)
