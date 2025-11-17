from django.urls import path

from .api import FamilyFullTreeAPIView, FamilyTreeAPIView, PeopleTablesDataAPIView

app_name = "people_api"

urlpatterns = [
    path("people/full/attributes/", PeopleTablesDataAPIView.as_view(), name="people-full-attributes"),
    path("families/", FamilyTreeAPIView.as_view(), name="family-tree"),
    path("families/<int:pk>/tree/", FamilyFullTreeAPIView.as_view(), name="family-full-tree"),
]
