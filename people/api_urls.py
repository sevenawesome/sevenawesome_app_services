from django.urls import path

from .api import FamilyFullTreeAPIView, FamilyTreeAPIView

app_name = "people_api"

urlpatterns = [
    path("families/", FamilyTreeAPIView.as_view(), name="family-tree"),
    path("families/<int:pk>/tree/", FamilyFullTreeAPIView.as_view(), name="family-full-tree"),
]
