from __future__ import annotations

from datetime import date
from typing import Iterable

from django.utils import timezone
from rest_framework import serializers

from .models import Family, FamilyMember, Person, PersonRelationship


def _years_between(start_date: date | None, end_date: date | None = None) -> int | None:
    """Return the completed years between two dates."""
    if not start_date:
        return None
    comparison_date = end_date or timezone.now().date()
    if comparison_date < start_date:
        return 0
    years = comparison_date.year - start_date.year
    if (comparison_date.month, comparison_date.day) < (start_date.month, start_date.day):
        years -= 1
    return years


def _string_name(name_obj) -> str | None:
    return name_obj.value if name_obj else None


def _string_last_name(last_name_obj) -> str | None:
    return last_name_obj.value if last_name_obj else None


def _code_label(instance) -> dict | None:
    if not instance:
        return None
    data: dict[str, object] = {"id": instance.id}
    if hasattr(instance, "code"):
        data["code"] = instance.code
    if hasattr(instance, "label"):
        data["label"] = instance.label
    elif hasattr(instance, "name"):
        data["label"] = instance.name
    else:
        data["label"] = str(instance)
    return data


def _location_payload(location) -> dict | None:
    if not location:
        return None
    return {
        "id": location.id,
        "name": location.name,
        "address_line1": location.address_line1,
        "address_line2": location.address_line2,
        "city": location.city.name if location.city_id else None,
        "state": location.state.name if location.state_id else None,
        "country": location.country.name if location.country_id else None,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "google_maps_url": location.google_maps_url,
        "waze_url": location.waze_url,
    }


def _country_payload(country) -> dict | None:
    if not country:
        return None
    return {"id": country.id, "code": country.code, "name": country.name}


def _state_payload(state) -> dict | None:
    if not state:
        return None
    return {
        "id": state.id,
        "name": state.name,
        "country": state.country.code if state.country_id else None,
    }


def _city_payload(city) -> dict | None:
    if not city:
        return None
    return {
        "id": city.id,
        "name": city.name,
        "state": city.state.name if city.state_id else None,
        "country": city.country.code if city.country_id else None,
    }


def _person_reference(person: Person | None) -> dict | None:
    if not person:
        return None
    return {
        "id": person.id,
        "full_name": str(person),
        "gender": _code_label(person.gender),
        "age_years": _years_between(person.date_of_birth),
    }


class PersonRelationshipSerializer(serializers.ModelSerializer):
    relationship_type = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()
    relationship_years = serializers.SerializerMethodField()
    is_current = serializers.BooleanField(source="is_current", read_only=True)

    class Meta:
        model = PersonRelationship
        fields = (
            "id",
            "relationship_type",
            "started_on",
            "ended_on",
            "relationship_years",
            "is_current",
            "notes",
            "partner",
        )

    def get_relationship_type(self, obj: PersonRelationship) -> dict | None:
        if not obj.relationship_type:
            return None
        return {
            "id": obj.relationship_type.id,
            "code": obj.relationship_type.code,
            "label": obj.relationship_type.label,
        }

    def get_partner(self, obj: PersonRelationship) -> dict | None:
        base_person: Person = self.context["person"]
        partner = obj.partner if obj.person_id == base_person.id else obj.person
        return _person_reference(partner)

    def get_relationship_years(self, obj: PersonRelationship) -> int | None:
        return _years_between(obj.started_on, obj.ended_on)


class PersonProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    second_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    second_last_name = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    identity_type = serializers.SerializerMethodField()
    marital_status = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()
    cause_of_death = serializers.SerializerMethodField()
    birth_country = serializers.SerializerMethodField()
    birth_state = serializers.SerializerMethodField()
    birth_city = serializers.SerializerMethodField()
    current_address = serializers.SerializerMethodField()
    relationships = serializers.SerializerMethodField()
    age_years = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = (
            "id",
            "full_name",
            "first_name",
            "second_name",
            "last_name",
            "second_last_name",
            "nickname",
            "gender",
            "identity_type",
            "identity",
            "email",
            "cellphone",
            "housephone",
            "date_of_birth",
            "age_years",
            "is_deceased",
            "date_of_death",
            "cause_of_death",
            "birth_country",
            "birth_state",
            "birth_city",
            "current_address",
            "education",
            "is_studing",
            "occupation",
            "is_employed",
            "marital_status",
            "created_date",
            "last_updated",
            "relationships",
        )

    def get_full_name(self, obj: Person) -> str:
        return str(obj)

    def get_first_name(self, obj: Person) -> str | None:
        return _string_name(obj.first_name)

    def get_second_name(self, obj: Person) -> str | None:
        return _string_name(obj.second_name)

    def get_last_name(self, obj: Person) -> str | None:
        return _string_last_name(obj.last_name)

    def get_second_last_name(self, obj: Person) -> str | None:
        return _string_last_name(obj.second_last_name)

    def get_nickname(self, obj: Person) -> str | None:
        return obj.nickname.value if obj.nickname_id else None

    def get_gender(self, obj: Person) -> dict | None:
        return _code_label(obj.gender)

    def get_identity_type(self, obj: Person) -> dict | None:
        return _code_label(obj.identity_type)

    def get_marital_status(self, obj: Person) -> dict | None:
        return _code_label(obj.marital_status)

    def get_education(self, obj: Person) -> dict | None:
        if not obj.education:
            return None
        return {
            "id": obj.education.id,
            "code": obj.education.code,
            "label": obj.education.label,
            "description": obj.education.description,
        }

    def get_occupation(self, obj: Person) -> dict | None:
        if not obj.occupation:
            return None
        return {
            "id": obj.occupation.id,
            "code": obj.occupation.code,
            "label": obj.occupation.label,
            "description": obj.occupation.description,
        }

    def get_cause_of_death(self, obj: Person) -> dict | None:
        if not obj.cause_of_death:
            return None
        return {
            "id": obj.cause_of_death.id,
            "code": obj.cause_of_death.code,
            "name": obj.cause_of_death.name,
        }

    def get_birth_country(self, obj: Person) -> dict | None:
        return _country_payload(obj.birth_country)

    def get_birth_state(self, obj: Person) -> dict | None:
        return _state_payload(obj.birth_state)

    def get_birth_city(self, obj: Person) -> dict | None:
        return _city_payload(obj.birth_city)

    def get_current_address(self, obj: Person) -> dict | None:
        return _location_payload(obj.current_address)

    def get_relationships(self, obj: Person) -> list[dict]:
        relationships: list[PersonRelationship] = []
        seen_ids: set[int] = set()
        for rel in _collect_relationships(obj):
            if rel.id in seen_ids:
                continue
            seen_ids.add(rel.id)
            relationships.append(rel)
        serializer = PersonRelationshipSerializer(
            sorted(
                relationships,
                key=lambda rel: (
                    rel.started_on or date.min,
                    rel.pk,
                ),
            ),
            many=True,
            context={"person": obj},
        )
        return serializer.data

    def get_age_years(self, obj: Person) -> int | None:
        return _years_between(obj.date_of_birth)


def _collect_relationships(person: Person) -> Iterable[PersonRelationship]:
    return (
        list(person.relationships_as_person.all())
        + list(person.relationships_as_partner.all())
    )


class FamilyMemberSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    person = PersonProfileSerializer(read_only=True)

    class Meta:
        model = FamilyMember
        fields = (
            "id",
            "role",
            "is_primary",
            "joined_date",
            "left_date",
            "notes",
            "person",
        )

    def get_role(self, obj: FamilyMember) -> dict:
        return {
            "id": obj.role.id,
            "code": obj.role.code,
            "name": obj.role.name,
        }


class FamilyTreeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    full_last_name = serializers.CharField(read_only=True)
    members = FamilyMemberSerializer(source="memberships", many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = (
            "id",
            "name",
            "full_last_name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
            "member_count",
            "members",
        )

    def get_member_count(self, obj: Family) -> int:
        prefetched = getattr(obj, "_prefetched_objects_cache", {}).get("memberships")
        if prefetched is not None:
            return len(prefetched)
        return obj.memberships.count()
