from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Family, FamilyMember, PersonRelationship
from .serializers import FamilyTreeSerializer


class FamilyTreeAPIView(generics.ListAPIView):
    """
    Return the list of families with their members (family tree) and
    the full profile of each person including relationships.
    """

    serializer_class = FamilyTreeSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Family.objects.all()
        if not self._should_include_inactive():
            queryset = queryset.filter(is_active=True)

        return (
            queryset.select_related(
                "first_last_name",
                "second_last_name",
                "third_last_name",
                "fourth_last_name",
            )
            .prefetch_related(
                Prefetch(
                    "memberships",
                    queryset=self._membership_queryset(),
                )
            )
            .order_by(
                "first_last_name__value",
                "second_last_name__value",
                "third_last_name__value",
                "fourth_last_name__value",
                "id",
            )
        )

    def _relationship_queryset(self):
        return (
            PersonRelationship.objects.select_related(
                "relationship_type",
                "person__first_name",
                "person__second_name",
                "person__last_name",
                "person__second_last_name",
                "person__gender",
                "partner__first_name",
                "partner__second_name",
                "partner__last_name",
                "partner__second_last_name",
                "partner__gender",
            )
            .order_by("-started_on", "-created_at")
        )

    def _membership_queryset(self):
        relationship_qs = self._relationship_queryset()
        return (
            FamilyMember.objects.select_related(
                "role",
                "person__first_name",
                "person__second_name",
                "person__last_name",
                "person__second_last_name",
                "person__nickname",
                "person__gender",
                "person__identity_type",
                "person__education",
                "person__occupation",
                "person__marital_status",
                "person__cause_of_death",
                "person__birth_country",
                "person__birth_state",
                "person__birth_city",
                "person__current_address",
                "person__current_address__country",
                "person__current_address__state",
                "person__current_address__city",
            )
            .prefetch_related(
                Prefetch(
                    "person__relationships_as_person",
                    queryset=relationship_qs,
                ),
                Prefetch(
                    "person__relationships_as_partner",
                    queryset=relationship_qs,
                ),
            )
            .order_by(
                "role__display_order",
                "person__first_name__value",
                "person__last_name__value",
                "person__id",
            )
        )

    def _should_include_inactive(self) -> bool:
        flag = self.request.query_params.get("include_inactive", "")
        return flag.lower() in {"true", "1", "yes"}
