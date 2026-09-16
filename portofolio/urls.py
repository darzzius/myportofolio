from django.contrib import admin
from django.urls import include, path
from main.views import (
   create_project
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("projects/add/", create_project, name="create_project"),
]