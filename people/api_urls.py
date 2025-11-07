from django.urls import path

from .api import FamilyTreeAPIView

app_name = "people_api"

urlpatterns = [
    path("families/", FamilyTreeAPIView.as_view(), name="family-tree"),
]
