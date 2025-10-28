from django.contrib import admin


from .models import Family, FamilyMember, FamilyRole


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ("person", "family", "role", "is_primary", "joined_date", "left_date")
    list_filter = ("role", "is_primary")
    search_fields = ("person__first_name", "person__last_name", "family__name")


@admin.register(FamilyRole)
class FamilyRoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")