from django.db import models
from django.db.models import Q
from django.utils import timezone
from people.models import Person

"""
class LearnAboutIASD(models.Model):
    code = models.CharField(max_length=20, unique=True)   # e.g., invitation, evangelism, radio
    label = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

    how_did_you_learn_about_iasd = models.ForeignKey(LearnAboutIASD,on_delete=models.SET_NULL,blank=True,null=True,related_name="people")


    baptism_date = models.DateField(blank=True, null=True)
    baptized_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="baptized_members",
    )

    class PersonStatus(models.Model):
    code = models.CharField(max_length=20, unique=True)   # e.g., Active, Inactive, Deceased, Transferred,dead
    label = models.CharField(max_length=50)               # display label
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.label

        status = models.ForeignKey(
        PersonStatus,
        on_delete=models.DO_NOTHING,
        related_name="people_with_status",
    )  
# --------------------------
# General Conference
# --------------------------
class GeneralConference(models.Model):
    # implicit PK: id
    name = models.CharField(max_length=150)
    organized_year = models.IntegerField(blank=True, null=True)
    territory = models.TextField(blank=True, null=True)
    churches = models.IntegerField(blank=True, null=True)
    membership = models.IntegerField(blank=True, null=True)
    population = models.BigIntegerField(blank=True, null=True)

    president = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="general_conferences_led",
        db_column="president_id",
    )

    phone = models.CharField(max_length=50, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    last_updated = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "general_conference"

    def __str__(self):
        return self.name


# --------------------------
# Division
# --------------------------
class Division(models.Model):
    # implicit PK: id
    name = models.CharField(max_length=150)
    gc = models.ForeignKey(
        GeneralConference,
        on_delete=models.PROTECT,
        related_name="divisions",
    )
    organized_year = models.IntegerField(blank=True, null=True)
    territory = models.TextField(blank=True, null=True)
    churches = models.IntegerField(blank=True, null=True)
    membership = models.IntegerField(blank=True, null=True)
    population = models.BigIntegerField(blank=True, null=True)

    president = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="divisions_led",
        db_column="president_id",
    )

    phone = models.CharField(max_length=50, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    last_updated = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "division"

    def __str__(self):
        return self.name


# --------------------------
# Union Conference
# --------------------------
class UnionConference(models.Model):
    # implicit PK: id
    name = models.CharField(max_length=150)
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        related_name="unions",
    )
    organized_year = models.IntegerField(blank=True, null=True)
    reorganized_year = models.IntegerField(blank=True, null=True)
    territory = models.TextField(blank=True, null=True)
    churches = models.IntegerField(blank=True, null=True)
    membership = models.IntegerField(blank=True, null=True)
    population = models.BigIntegerField(blank=True, null=True)

    president = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="unions_presided",
        db_column="president_id",
    )
    secretary = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="unions_secretaried",
        db_column="secretary_id",
    )
    treasurer = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="unions_treasuried",
        db_column="treasurer_id",
    )

    phone = models.CharField(max_length=50, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    mailing_address = models.CharField(max_length=250, blank=True, null=True)
    last_updated = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "union_conference"

    def __str__(self):
        return self.name


# --------------------------
# Field Conference
# --------------------------
class FieldConference(models.Model):
    class ConferenceType(models.TextChoices):
        CONFERENCE = "Conference", "Conference"
        MISSION = "Mission", "Mission"
        OTHER = "Other", "Other"

    # implicit PK: id
    name = models.CharField(max_length=150)
    union = models.ForeignKey(
        UnionConference,
        on_delete=models.PROTECT,
        related_name="fields",
    )
    type = models.CharField(max_length=50, choices=ConferenceType.choices, blank=True, null=True)
    organized_year = models.IntegerField(blank=True, null=True)
    reorganized_year = models.IntegerField(blank=True, null=True)
    territory = models.TextField(blank=True, null=True)
    churches = models.IntegerField(blank=True, null=True)
    membership = models.IntegerField(blank=True, null=True)
    population = models.BigIntegerField(blank=True, null=True)

    president = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fields_presided",
        db_column="president_id",
    )
    secretary = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fields_secretaried",
        db_column="secretary_id",
    )
    treasurer = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fields_treasuried",
        db_column="treasurer_id",
    )

    phone = models.CharField(max_length=100, blank=True, null=True)
    fax = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    mailing_address = models.CharField(max_length=250, blank=True, null=True)
    last_updated = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "field_conference"

    def __str__(self):
        return self.name


# --------------------------
# Church
# --------------------------
class Church(models.Model):
    class ChurchType(models.TextChoices):
        CHURCH = "Church", "Church"
        COMPANY = "Company", "Company"
        GROUP = "Group", "Group"
        OTHER = "Other", "Other"

    # implicit PK: id
    name = models.CharField(max_length=150)
    conference = models.ForeignKey(
        FieldConference,
        on_delete=models.PROTECT,
        related_name="church_set",
    )
    members = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=50, choices=ChurchType.choices, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)

    pastor = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="churches_pastored",
        db_column="pastor_id",
    )

    last_updated = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "church"

    def __str__(self):
        return self.name
"""