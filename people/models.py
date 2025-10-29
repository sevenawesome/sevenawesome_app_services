from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

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
    
class Nationality(models.Model):
    code = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)   # e.g., es, en, fr
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

class Country(models.Model):
    code = models.CharField(max_length=5, unique=True)   # e.g., DO, US
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
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=100)
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
    name = models.CharField(max_length=100)
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
    
class  Occupation(models.Model):
    code = models.CharField(max_length=20, unique=True)   # e.g., DF,PL,AC
    label = models.CharField(max_length=50)   # display label plomero,ama de casa..
    description = models.CharField(max_length=300, blank=True, null=True)            
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.label
    
# --------------------------
# Person
# --------------------------

class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
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
    occupation = models.ForeignKey(
        Occupation,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="people_with_occupation",
    )
    marital_status = models.ForeignKey(
        MaritalStatus,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="people_with_marital_status",
    )
    photo = models.CharField(max_length=400, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_email = models.EmailField(blank=True, null=True)
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
        return f"{self.first_name} {self.last_name}"

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

    def spouse_history(self):
        return self.get_marriages().order_by("-married_on")

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
        db_table = "marriage"
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


class Family(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f"Family #{self.pk}"


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
        return f"{self.person} - {self.get_role_display()} of {self.family}"


