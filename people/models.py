from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

DATING_RELATIONSHIP_CODE = "dating"

# --------------------------
# Lookup tables
# --------------------------

class Gender(models.Model):
    code = models.CharField(max_length=10, unique=True)   # e.g., M, F
    label = models.CharField(max_length=50)               # e.g., Male, Famele
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

class MaritalStatus(models.Model):
    code = models.CharField(max_length=20, unique=True)   # e.g., single, married, divorced
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

class MarriageEndReason(models.Model):
    code = models.CharField(max_length=20, unique=True)   # e.g., divorced, widowed
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label
    

class RelationshipType(models.Model):
    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "label")

    def __str__(self):
        return self.label


class PersonAttributeType(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "name")

    def __str__(self):
        return self.name

class Nationality(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

class Language(models.Model):
    code = models.CharField(max_length=100, unique=True)   # e.g., es, en, fr
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

class Country(models.Model):
    code = models.CharField(max_length=100, unique=True)   # e.g., DO, US
    name = models.CharField(max_length=100)
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people_with_nationality",
    )
    native_language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="countries_as_native_language",
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class State(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="states",
    )
    code = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.name}, {self.country.code}"


class City(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities",
    )
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="cities",
    )
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.name}, {self.state.name}"


class Location(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    address_line1 = models.CharField(max_length=150, blank=True, null=True)
    address_line2 = models.CharField(max_length=150, blank=True, null=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="locations",
    )
    state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="locations",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="locations",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    google_maps_url = models.URLField(blank=True, null=True)
    waze_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return self.name
        if self.latitude is not None and self.longitude is not None:
            return f"{self.latitude}, {self.longitude}"
        return "Location"

class SocialNetworkPlatform(models.Model):
    code = models.CharField(max_length=30, unique=True)   # e.g., facebook, instagram
    name = models.CharField(max_length=100)
    url_pattern = models.CharField(max_length=255,blank=True,null=True,)  # optional reference pattern, e.g., https://instagram.com/{handle}
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name
        
class PersonIdentityType(models.Model):
    code = models.CharField(max_length=20, unique=True)   # e.g., C,P
    label = models.CharField(max_length=50)               # display label cedula,pasaporte,id
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.label

class EducationalLevel(models.Model):
    code = models.CharField(max_length=20, unique=True)   # e.g., B,P,MA,DR
    label = models.CharField(max_length=50) # display label primaria,secundaria,basica,bachiller,profesional...
    description = models.CharField(max_length=300, blank=True, null=True)    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.label
    
class Degree(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="institutions",
    )
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
    
class Occupation(models.Model):
    code = models.CharField(max_length=150, unique=True)   # e.g., DF,PL,AC
    label = models.CharField(max_length=150)   # display label plomero,ama de casa..
    description = models.CharField(max_length=300, blank=True, null=True)            
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.label
    
class DeathCause(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
# --------------------------
# Name catalog
# --------------------------

class PersonName(models.Model):
    value = models.CharField(max_length=100, unique=True) # value keeps the name exactly as entered so you can preserve capitalization and accents for display
    normalized_value = models.CharField(max_length=100, unique=True, editable=False) # normalized_value is the lowercase, trimmed version that the model writes just before saving
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("normalized_value",)

    def __str__(self):
        return self.value

    def save(self, *args, **kwargs):
        normalized = (self.value or "").strip().lower()
        self.normalized_value = normalized
        super().save(*args, **kwargs)


class LastName(models.Model):
    value = models.CharField(max_length=150, unique=True)
    normalized_value = models.CharField(max_length=150, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("normalized_value",)

    def __str__(self):
        return self.value

    def save(self, *args, **kwargs):
        normalized = (self.value or "").strip().lower()
        self.normalized_value = normalized
        super().save(*args, **kwargs)


class Nickname(models.Model):
    value = models.CharField(max_length=100, unique=True)
    normalized_value = models.CharField(max_length=100, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("normalized_value",)

    def __str__(self):
        return self.value

    def save(self, *args, **kwargs):
        normalized = (self.value or "").strip().lower()
        self.normalized_value = normalized
        super().save(*args, **kwargs)

# --------------------------
# Person
# --------------------------

class Person(models.Model):
    first_name = models.ForeignKey(
        PersonName,
        on_delete=models.PROTECT,
        related_name="people_with_first_name",
    )
    second_name = models.ForeignKey(
        PersonName,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people_with_second_name",
    )
    last_name = models.ForeignKey(
        LastName,
        on_delete=models.PROTECT,
        related_name="people_with_last_name",
    )
    second_last_name = models.ForeignKey(
        LastName,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people_with_second_last_name",
    )
    nickname = models.ForeignKey(
        Nickname,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people",
    )
    identity_type = models.ForeignKey(
        PersonIdentityType,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="people_with_identity_type",
    )
    identity = models.CharField(max_length=100, blank=True, null=True)   
    gender = models.ForeignKey(
        Gender,
        on_delete=models.DO_NOTHING,
        related_name="people",
    )
    email = models.EmailField(blank=True, null=True)
    cellphone = models.CharField(max_length=50, blank=True, null=True)
    housephone = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_deceased = models.BooleanField(default=False)
    date_of_death = models.DateField(blank=True, null=True)
    cause_of_death = models.ForeignKey(
        DeathCause,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="deceased_people",
    )
    birth_country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people_current_country",
    )
    birth_state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people_in_state",
    )
    birth_city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people_in_city",
    )
    current_address = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people",
    )
    education = models.ForeignKey(
        EducationalLevel,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="people_with_education",
    )
    is_studing = models.BooleanField(default=False)
    occupation = models.ForeignKey(
        Occupation,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="people_with_occupation",
    )
    is_employed = models.BooleanField(default=False)
    marital_status = models.ForeignKey(
        MaritalStatus,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people_with_marital_status",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="person_profile",
    )
    created_date = models.DateField(default=timezone.now, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        first = self.first_name.value if self.first_name_id else ""
        last = self.last_name.value if self.last_name_id else ""
        return f"{first} {last}".strip()

    def get_family_members(self, role_codes=None):
        """
        Return a queryset of the person's relatives within shared families.
        Optionally filter by the relative's role (matched by role code) inside those families.
        """
        queryset = (
            Person.objects.filter(
                family_memberships__family__memberships__person=self,
            )
            .exclude(pk=self.pk)
        )
        if role_codes:
            queryset = queryset.filter(
                family_memberships__role__code__in=role_codes,
                family_memberships__family__memberships__person=self,
            )
        return queryset.distinct()

    def parents(self):
        return self.get_family_members(
            role_codes=[
                "mother",
                "father",
                "guardian",
            ]
        )

    def siblings(self):
        return self.get_family_members(
            role_codes=[
                "child",
                "sibling",
            ]
        )

    def children(self):
        return Person.objects.filter(
            family_memberships__family__memberships__person=self,
            family_memberships__role__code__in=[
                "child",
            ],
            family_memberships__family__memberships__role__code__in=[
                "father",
                "mother",
                "guardian",
                "spouse",
            ],
        ).distinct()

    def get_marriages(self):
        """Return all marriages involving this person ordered by start date."""
        return Marriage.objects.filter(
            Q(husband=self) | Q(wife=self),
        ).order_by("married_on")

    def current_marriage(self):
        return (
            self.get_marriages()
            .filter(ended_on__isnull=True)
            .order_by("-married_on")
            .first()
        )

    def current_spouse(self):
        marriage = self.current_marriage()
        if not marriage:
            return None
        return marriage.husband if marriage.wife_id == self.pk else marriage.wife

    def dating_relationships(self):
        """Return dating relationships (current and past) involving this person."""
        return PersonRelationship.objects.filter(
            Q(person=self) | Q(partner=self),
            relationship_type__code=DATING_RELATIONSHIP_CODE,
        ).select_related("relationship_type")

    def current_dating_relationship(self):
        """Return the active dating relationship, if any."""
        return (
            self.dating_relationships()
            .filter(ended_on__isnull=True)
            .order_by("-started_on", "-created_at")
            .select_related("person", "partner")
            .first()
        )

    def current_dating_partner(self):
        """Return the partner in the active dating relationship."""
        relationship = self.current_dating_relationship()
        if not relationship:
            return None
        if relationship.person_id == self.pk:
            return relationship.partner
        return relationship.person

    @property
    def has_boyfriend_or_girlfriend(self):
        """Convenience flag indicating whether a dating relationship exists."""
        return self.current_dating_partner() is not None

    def get_attribute_assignments(self, include_inactive=False):
        """
        Return attribute assignments for the person.
        By default only current (non-ended) assignments are returned.
        """
        assignments = self.attribute_assignments.select_related(
            "attribute",
            "attribute__attribute_type",
        ).order_by(
            "attribute__attribute_type__order",
            "attribute__attribute_type__name",
            "attribute__order",
            "attribute__name",
        )
        if include_inactive:
            return assignments
        return assignments.filter(ended_on__isnull=True)

    def attributes(self, include_inactive=False):
        """
        Return a queryset of PersonAttribute instances associated with the person.
        """
        filters = {}
        if not include_inactive:
            filters["person_assignments__ended_on__isnull"] = True
        return (
            PersonAttribute.objects.filter(
                person_assignments__person=self,
                **filters,
            )
            .select_related("attribute_type")
            .order_by(
                "attribute_type__order",
                "attribute_type__name",
                "order",
                "name",
            )
            .distinct()
        )

    def spouse_history(self):
        return self.get_marriages().order_by("-married_on")

    def latest_photo(self):
        """Return the most recent photo, prioritizing any marked as primary."""
        return (
            self.photos.filter(is_primary=True)
            .order_by("-captured_on", "-created_at")
            .first()
            or self.photos.order_by("-captured_on", "-created_at").first()
        )

    def primary_emergency_contact(self):
        """Return the contact explicitly marked as primary, if any."""
        return self.emergency_contacts.filter(is_primary=True).first()

    def current_health_status(self):
        """Return the health status flagged as current or the most recent record."""
        return (
            self.health_statuses.filter(is_current=True)
            .order_by("-diagnosed_on", "-created_at")
            .first()
            or self.health_statuses.order_by("-diagnosed_on", "-created_at").first()
        )

    def health_status_history(self):
        """Return all health status records ordered from most to least recent."""
        return self.health_statuses.order_by("-diagnosed_on", "-created_at")

    @property
    def is_alive(self):
        return not self.is_deceased

    def death_details(self):
        """Return (date, cause) tuple if the person is marked as deceased."""
        if not self.is_deceased:
            return None
        cause = self.cause_of_death.name if self.cause_of_death else None
        return self.date_of_death, cause

    def degree_history(self):
        """Return all recorded degree studies ordered by most recent completion."""
        return self.person_degrees.select_related("degree").order_by(
            "-end_year",
            "-start_year",
            "degree__name",
        )

    def current_degrees(self):
        """Return degree records that are still in progress."""
        return self.person_degrees.select_related("degree").filter(is_completed=False)


class PersonPhoto(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    image_url = models.CharField(max_length=400)
    image_name = models.CharField(max_length=400)
    captured_on = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "-is_primary",
            "-captured_on",
            "-created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("person",),
                condition=Q(is_primary=True),
                name="unique_primary_photo_per_person",
            ),
        ]

    def __str__(self):
        when = self.captured_on.isoformat() if self.captured_on else "undated"
        return f"{self.person} photo ({when})"

class PersonAttribute(models.Model):
    attribute_type = models.ForeignKey(
        PersonAttributeType,
        on_delete=models.PROTECT,
        related_name="attributes",
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="person_attributes",
        blank=True,
        null=True,
    )
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = (
            "attribute_type__order",
            "attribute_type__name",
            "order",
            "name",
        )

    def __str__(self):
        return self.name

class PersonEmergencyContact(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )
    name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "-is_primary",
            "name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("person",),
                condition=Q(is_primary=True),
                name="unique_primary_emergency_contact_per_person",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.person})"


class HealthCondition(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class PersonHealthStatus(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="health_statuses",
    )
    condition = models.ForeignKey(
        HealthCondition,
        on_delete=models.PROTECT,
        related_name="people_with_condition",
    )
    description = models.TextField(blank=True, null=True)
    diagnosed_on = models.DateField(blank=True, null=True)
    resolved_on = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "-is_current",
            "-diagnosed_on",
            "-created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("person",),
                condition=Q(is_current=True),
                name="unique_current_health_status_per_person",
            ),
        ]

    def __str__(self):
        when = self.diagnosed_on.isoformat() if self.diagnosed_on else "undated"
        return f"{self.person} - {self.condition.name} ({when})"


class PersonDegree(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="person_degrees",
    )
    degree = models.ForeignKey(
        Degree,
        on_delete=models.PROTECT,
        related_name="people_with_degree",
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.PROTECT,
        related_name="person_degrees",
        blank=True,
        null=True,
    )
    field_of_study = models.CharField(max_length=150, blank=True, null=True)
    start_year = models.PositiveIntegerField(blank=True, null=True)
    end_year = models.PositiveIntegerField(blank=True, null=True)
    is_completed = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "-end_year",
            "-start_year",
            "degree__name",
        )

    def __str__(self):
        period = []
        if self.start_year:
            period.append(str(self.start_year))
        if self.end_year:
            period.append(str(self.end_year))
        years = "-".join(period) if period else "unspecified"
        institution = f" @ {self.institution}" if self.institution else ""
        return f"{self.person} - {self.degree.name}{institution} ({years})"


class LanguagesProficiencyLevels(models.Model):
    code = models.CharField(max_length=20, unique=True)   # Beginner (A1),Elementary (A2)
    label = models.CharField(max_length=50)   # display label Can understand and use basic phrases. Limited vocabulary and grammar.
    description = models.CharField(max_length=300, blank=True, null=True)            
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.label
    """
        Beginner (A1): Can understand and use basic phrases. Limited vocabulary and grammar.
        Elementary (A2): Can handle simple conversations and write short texts.
        Intermediate (B1): Can deal with everyday situations, express opinions, and understand main ideas.
        Upper Intermediate (B2): Can interact fluently, understand complex texts, and write detailed content.
        Advanced (C1): Can use the language effectively in professional and academic settings.
        Proficient/Fluent (C2): Near-native level. Can understand virtually everything and express themselves effortlessly.
        Native: Learned the language from birth. Full cultural and linguistic fluency.
    
    """

class PersonLanguages(models.Model):
    person = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="person_languages",)
    language = models.ForeignKey(Language,on_delete=models.CASCADE,related_name="people_preferred_languages")
    language_proficiency_level = models.ForeignKey(LanguagesProficiencyLevels,on_delete=models.CASCADE, related_name="people_proficiency_level")
    is_preferred = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        identifier = self.handle or self.url or ""
        return f"{self.person} on {self.platform}{f' ({identifier})' if identifier else ''}"


class PersonSocialNetwork(models.Model):
    person = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="social_profiles",)
    platform = models.ForeignKey(SocialNetworkPlatform,on_delete=models.CASCADE,related_name="person_profiles",)
    handle = models.CharField(max_length=150, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        identifier = self.handle or self.url or ""
        return f"{self.person} on {self.platform}{f' ({identifier})' if identifier else ''}"


class Marriage(models.Model):
    husband = models.ForeignKey(Person, on_delete=models.CASCADE,related_name="marriages_as_husband")
    wife = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="marriages_as_wife")
    married_on = models.DateField()
    ended_on = models.DateField(blank=True, null=True)
    end_reason = models.ForeignKey(MarriageEndReason,on_delete=models.SET_NULL,blank=True,null=True,related_name="marriages",)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-married_on",)
        constraints = [
            models.UniqueConstraint(
                fields=("husband",),
                condition=Q(ended_on__isnull=True),
                name="unique_active_marriage_husband",
            ),
            models.UniqueConstraint(
                fields=("wife",),
                condition=Q(ended_on__isnull=True),
                name="unique_active_marriage_wife",
            ),
        ]

    def __str__(self):
        return f"{self.husband} & {self.wife} ({self.married_on:%Y-%m-%d})"

    @property
    def is_active(self):
        return self.ended_on is None


class PersonRelationship(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="relationships_as_person",
    )
    partner = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="relationships_as_partner",
    )
    relationship_type = models.ForeignKey(
        RelationshipType,
        on_delete=models.PROTECT,
        related_name="relationships",
    )
    started_on = models.DateField(blank=True, null=True)
    ended_on = models.DateField(blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-started_on", "-created_at")
        constraints = [
            models.CheckConstraint(
                check=~Q(person=F("partner")),
                name="prevent_self_relationship",
            ),
            models.UniqueConstraint(
                fields=("person", "partner", "relationship_type"),
                condition=Q(ended_on__isnull=True),
                name="unique_active_relationship_pair",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.person_id and self.partner_id and self.person_id > self.partner_id:
            self.person_id, self.partner_id = self.partner_id, self.person_id
        super().save(*args, **kwargs)

    def __str__(self):
        status = "ended" if self.ended_on else "current"
        label = self.relationship_type.label if self.relationship_type else "Unspecified"
        return f"{self.person} & {self.partner} - {label} ({status})"

    @property
    def is_current(self):
        return self.ended_on is None


class PersonAttributeAssignment(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="attribute_assignments",
    )
    attribute = models.ForeignKey(
        PersonAttribute,
        on_delete=models.PROTECT,
        related_name="person_assignments",
    )
    proficiency = models.CharField(max_length=100, blank=True, null=True)
    started_on = models.DateField(blank=True, null=True)
    ended_on = models.DateField(blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-started_on", "-created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("person", "attribute"),
                condition=Q(ended_on__isnull=True),
                name="unique_active_attribute_per_person",
            ),
        ]

    def __str__(self):
        status = "ended" if self.ended_on else "current"
        return f"{self.person} - {self.attribute} ({status})"

    @property
    def is_current(self):
        return self.ended_on is None


class Family(models.Model):
    first_last_name = models.ForeignKey(
        LastName,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="families_as_first_last_name",
    )
    second_last_name = models.ForeignKey(
        LastName,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="families_as_second_last_name",
    )
    third_last_name = models.ForeignKey(
        LastName,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="families_as_third_last_name",
    )
    fourth_last_name = models.ForeignKey(
        LastName,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="families_as_fourth_last_name",
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_last_name(self):
        parts = (
            self.first_last_name.value if self.first_last_name_id else None,
            self.second_last_name.value if self.second_last_name_id else None,
            self.third_last_name.value if self.third_last_name_id else None,
            self.fourth_last_name.value if self.fourth_last_name_id else None,
        )
        return " ".join(part for part in parts if part)

    @property
    def name(self):
        return self.full_last_name

    def __str__(self):
        return self.full_last_name or f"Family #{self.pk}"


class FamilyRole(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class FamilyMember(models.Model):

    family = models.ForeignKey(Family,on_delete=models.CASCADE,related_name="memberships",)
    person = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="family_memberships",)
    role = models.ForeignKey(FamilyRole,on_delete=models.PROTECT,related_name="family_members",)
    is_primary = models.BooleanField(default=False)
    joined_date = models.DateField(blank=True, null=True)
    left_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person} - {self.role} of {self.family}"
    



