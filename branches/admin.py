# branches/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Branch, UserBranch

# Inline for selecting branch on the user edit page
class UserBranchInline(admin.StackedInline):
    model = UserBranch
    can_delete = False
    verbose_name = "Branch"
    verbose_name_plural = "Branch"
    fk_name = "user"
    extra = 0

class CustomUserAdmin(UserAdmin):
    inlines = (UserBranchInline,)

    # show branch on the user list
    def branch(self, obj):
        try:
            return obj.branch_assignment.branch.name if obj.branch_assignment and obj.branch_assignment.branch else "-"
        except Exception:
            return "-"
    branch.short_description = "Branch"

    # add branch column to the existing user list_display
    list_display = UserAdmin.list_display + ("branch",)

# Re-register User with our custom admin ONLY if not already replaced
try:
    admin.site.unregister(User)
except Exception:
    pass
admin.site.register(User, CustomUserAdmin)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "address", "created_at")
    search_fields = ("name", "city")
    list_filter = ("city",)