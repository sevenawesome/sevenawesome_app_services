from django.db.models import Prefetch
from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
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


class FamilyFullTreeAPIView(APIView):
    """
    Return the full family tree graph starting from a given family id.
    It walks across all families that any member belongs to (paternal, maternal,
    married/partner families, etc.) until no new families are found.
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = FamilyTreeSerializer

    def get(self, request, *args, **kwargs):
        include_inactive = self._should_include_inactive()
        starting_pk = kwargs.get("pk")
        root_family = self._family_queryset(include_inactive).filter(pk=starting_pk).first()
        if not root_family:
            raise Http404("Family not found.")

        visited: set[int] = set()
        enqueued: set[int] = {root_family.pk}
        queue: list[Family] = [root_family]
        families_payload: list[dict] = []
        connections: list[dict] = []
        seen_connections: set[tuple[int, int, int]] = set()

        while queue:
            family = queue.pop(0)
            if family.pk in visited:
                continue
            visited.add(family.pk)

            families_payload.append(self.serializer_class(family).data)

            for membership in family.memberships.all():
                person = membership.person
                for other_membership in person.family_memberships.all():
                    other_family = other_membership.family
                    if not include_inactive and not other_family.is_active:
                        continue
                    if other_family.pk == family.pk:
                        continue

                    connection_key = (person.pk, family.pk, other_family.pk)
                    if connection_key not in seen_connections:
                        seen_connections.add(connection_key)
                        connections.append(
                            {
                                "person_id": person.pk,
                                "person_full_name": str(person),
                                "from_family_id": family.pk,
                                "to_family_id": other_family.pk,
                                "role_in_to_family": other_membership.role.code,
                                "role_in_to_family_name": other_membership.role.name,
                                "is_primary_in_to_family": other_membership.is_primary,
                            }
                        )

                    if other_family.pk not in enqueued:
                        enqueued.add(other_family.pk)
                        try:
                            next_family = self._family_queryset(include_inactive).get(pk=other_family.pk)
                        except Family.DoesNotExist:
                            continue
                        queue.append(next_family)

        return Response(
            {
                "root_family_id": root_family.pk,
                "family_count": len(families_payload),
                "include_inactive": include_inactive,
                "families": families_payload,
                "connections": connections,
            }
        )

    def _family_queryset(self, include_inactive: bool):
        queryset = Family.objects.all()
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        return queryset.select_related(
            "first_last_name",
            "second_last_name",
            "third_last_name",
            "fourth_last_name",
        ).prefetch_related(
            Prefetch(
                "memberships",
                queryset=self._membership_queryset(include_inactive),
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

    def _person_family_memberships_queryset(self, include_inactive: bool):
        qs = FamilyMember.objects.select_related(
            "family",
            "family__first_last_name",
            "family__second_last_name",
            "family__third_last_name",
            "family__fourth_last_name",
            "role",
        ).order_by(
            "role__display_order",
            "family__first_last_name__value",
            "family__second_last_name__value",
            "family__third_last_name__value",
            "family__fourth_last_name__value",
            "family__id",
        )
        if not include_inactive:
            qs = qs.filter(family__is_active=True)
        return qs

    def _membership_queryset(self, include_inactive: bool):
        relationship_qs = self._relationship_queryset()
        person_family_memberships_qs = self._person_family_memberships_queryset(include_inactive)
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
                Prefetch(
                    "person__family_memberships",
                    queryset=person_family_memberships_qs,
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
