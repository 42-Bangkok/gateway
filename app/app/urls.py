"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from appaccount.api import router as account_router
from appdata.api import router as data_router
from apptasks.api import router as tasks_router

api = NinjaAPI()
api.add_router("/account", account_router)
api.add_router("/data", data_router)
api.add_router("/apptasks", tasks_router)

urlpatterns = [
    path("api/", api.urls),
    path("admin/", admin.site.urls),
]
