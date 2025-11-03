from django.contrib import admin


from .models import Family, FamilyMember, FamilyRole


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("id", "display_last_name", "is_active", "created_at")
    search_fields = (
        "first_last_name__value",
        "second_last_name__value",
        "third_last_name__value",
        "fourth_last_name__value",
    )
    list_filter = ("is_active",)

    def display_last_name(self, obj):
        return obj.full_last_name or f"Family #{obj.pk}"

    display_last_name.short_description = "Family last names"


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ("person", "family", "role", "is_primary", "joined_date", "left_date")
    list_filter = ("role", "is_primary")
    search_fields = (
        "person__first_name__value",
        "person__last_name__value",
        "family__first_last_name__value",
        "family__second_last_name__value",
        "family__third_last_name__value",
        "family__fourth_last_name__value",
    )


@admin.register(FamilyRole)
class FamilyRoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
