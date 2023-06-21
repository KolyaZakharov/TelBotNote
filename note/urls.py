from django.urls import path, include
from rest_framework import routers

from note.views import NoteViewSet

router = routers.DefaultRouter()
router.register("notes", NoteViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "note"
