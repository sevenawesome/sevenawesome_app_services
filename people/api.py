from django.db.models import Prefetch
from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import (
    City,
    Country,
    EducationalLevel,
    Family,
    FamilyMember,
    FamilyRole,
    Gender,
    Language,
    LastName,
    Location,
    MaritalStatus,
    Nationality,
    Nickname,
    Occupation,
    PersonIdentityType,
    PersonName,
    PersonRelationship,
    State,
)
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


class PeopleTablesDataAPIView(APIView):
    """
    Return flat exports for the requested people-related tables.
    Defaults to active records when models expose an `is_active` flag.
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        include_inactive = self._should_include_inactive()
        active_only = not include_inactive
        return Response(
            {
                "person_names": self._values_for(PersonName, active_only),
                "last_names": self._values_for(LastName, active_only),
                "families": self._families_payload(active_only),
                "family_roles": self._values_for(FamilyRole, active_only),
                "nicknames": self._values_for(Nickname, active_only),
                "person_identity_types": self._values_for(PersonIdentityType, active_only),
                "countries": self._countries_with_states_and_cities(active_only),
                "nationalities": self._values_for(Nationality, active_only),
                "languages": self._values_for(Language, active_only),
                "educational_levels": self._values_for(EducationalLevel, active_only),
                "genders": self._values_for(Gender, active_only),
                "marital_statuses": self._values_for(MaritalStatus, active_only),
                "occupations": self._values_for(Occupation, active_only),
                "locations": self._locations_payload(),
            }
        )

    def _values_for(self, model, active_only: bool):
        queryset = model.objects.all().order_by("id")
        if active_only and self._has_is_active(model):
            queryset = queryset.filter(is_active=True)
        return list(queryset.values())

    def _countries_with_states_and_cities(self, active_only: bool):
        city_qs = City.objects.all().order_by("id")
        if active_only:
            city_qs = city_qs.filter(is_active=True)

        state_qs = State.objects.all().order_by("id").prefetch_related(
            Prefetch("cities", queryset=city_qs)
        )
        if active_only:
            state_qs = state_qs.filter(is_active=True)

        country_qs = Country.objects.all().order_by("id").prefetch_related(
            Prefetch("states", queryset=state_qs)
        )
        if active_only:
            country_qs = country_qs.filter(is_active=True)

        payload = []
        for country in country_qs:
            payload.append(
                {
                    "id": country.id,
                    "code": country.code,
                    "name": country.name,
                    "is_active": getattr(country, "is_active", None),
                    "native_language": self._language_payload(country.native_language),
                    "nationality": self._nationality_payload(country.nationality),
                    "states": [
                        {
                            "id": state.id,
                            "code": state.code,
                            "name": state.name,
                            "is_active": getattr(state, "is_active", None),
                            "cities": [
                                {
                                    "id": city.id,
                                    "name": city.name,
                                    "is_active": getattr(city, "is_active", None),
                                }
                                for city in state.cities.all()
                            ],
                        }
                        for state in country.states.all()
                    ],
                }
            )
        return payload

    def _locations_payload(self):
        qs = (
            Location.objects.select_related("country", "state", "city")
            .all()
            .order_by("id")
        )
        payload = []
        for location in qs:
            payload.append(
                {
                    "id": location.id,
                    "name": location.name,
                    "description": location.description,
                    "address_line1": location.address_line1,
                    "address_line2": location.address_line2,
                    "country_id": location.country_id,
                    "country_name": location.country.name if location.country_id else None,
                    "state_id": location.state_id,
                    "state_name": location.state.name if location.state_id else None,
                    "city_id": location.city_id,
                    "city_name": location.city.name if location.city_id else None,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "google_maps_url": location.google_maps_url,
                    "waze_url": location.waze_url,
                    "notes": location.notes,
                    "created_at": location.created_at,
                    "updated_at": location.updated_at,
                }
            )
        return payload

    def _families_payload(self, active_only: bool):
        qs = (
            Family.objects.all()
            .select_related(
                "first_last_name",
                "second_last_name",
                "third_last_name",
                "fourth_last_name",
            )
            .order_by("id")
        )
        if active_only:
            qs = qs.filter(is_active=True)

        def _ln_value(last_name_obj):
            return last_name_obj.value if last_name_obj else None

        def _ln_data(last_name_obj):
            if not last_name_obj:
                return None
            return {
                "id": last_name_obj.id,
                "value": last_name_obj.value,
                "normalized_value": last_name_obj.normalized_value,
            }

        payload = []
        for family in qs:
            payload.append(
                {
                    "id": family.id,
                    "description": family.description,
                    "is_active": getattr(family, "is_active", None),
                    "created_at": family.created_at,
                    "updated_at": family.updated_at,
                    "first_last_name_id": family.first_last_name_id,
                    "second_last_name_id": family.second_last_name_id,
                    "third_last_name_id": family.third_last_name_id,
                    "fourth_last_name_id": family.fourth_last_name_id,
                    "first_last_name": _ln_value(family.first_last_name),
                    "second_last_name": _ln_value(family.second_last_name),
                    "third_last_name": _ln_value(family.third_last_name),
                    "fourth_last_name": _ln_value(family.fourth_last_name),
                    "first_last_name_data": _ln_data(family.first_last_name),
                    "second_last_name_data": _ln_data(family.second_last_name),
                    "third_last_name_data": _ln_data(family.third_last_name),
                    "fourth_last_name_data": _ln_data(family.fourth_last_name),
                }
            )
        return payload

    def _language_payload(self, language):
        if not language:
            return None
        return {"id": language.id, "code": language.code, "label": language.label}

    def _nationality_payload(self, nationality):
        if not nationality:
            return None
        return {"id": nationality.id, "code": nationality.code, "label": nationality.label}

    def _has_is_active(self, model) -> bool:
        return any(field.name == "is_active" for field in model._meta.fields)

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
