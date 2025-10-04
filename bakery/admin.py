from django.contrib import admin
from .forms import InventoryForm
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin, GroupAdmin as DefaultGroupAdmin
from django.contrib.auth.models import User, Group
from .models import Bread, Injera, Flour, Yeast, Enhancer, Inventory
from branches.models import Branch, UserBranch

# ------------------- Bakery Products Admin -------------------
@admin.register(Bread)
class BreadAdmin(admin.ModelAdmin):
    list_display = ("name", "flour_kg", "yeast_kg", "enhancer_kg", "water_birr", "electricity_birr", "selling_price","description")
    search_fields = ("name",)


@admin.register(Injera)
class InjeraAdmin(admin.ModelAdmin):
    list_display = ("name", "flour_kg", "yeast_kg", "water_birr", "electricity_birr", "selling_price","description")
    search_fields = ("name",)


@admin.register(Flour)
class FlourAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "cost_per_kg", "description")
    search_fields = ("name", "brand")


@admin.register(Yeast)
class YeastAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "cost_per_kg", "description")
    search_fields = ("name", "brand")


@admin.register(Enhancer)
class EnhancerAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "cost_per_kg", "description")
    search_fields = ("name", "brand")


# ------------------- Inventory Admin -------------------
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    form = InventoryForm

    def quantity_with_unit(self, obj):
        """Display quantity with appropriate units."""
        if obj.product_type in ['bread', 'injera']:
            return f"{obj.quantity} unit"
        elif obj.product_type in ['flour', 'yeast', 'enhancer']:
            return f"{obj.quantity} kg"
        return obj.quantity

    quantity_with_unit.short_description = "Quantity"

    list_display = ('branch', 'product_type', 'product_name', 'quantity_with_unit', 'last_updated')
    list_filter = ('branch', 'product_type', 'product_name')
    search_fields = ('product_name',)

    class Media:
        js = ('bakery/js/inventory.js',)


# ------------------- Superuser Only Admin Mixin -------------------
class SuperuserOnlyAdminMixin:
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ------------------- User Branch Inline -------------------
class UserBranchInline(admin.StackedInline):
    model = UserBranch
    can_delete = False
    verbose_name = "Branch"
    verbose_name_plural = "Branch"
    fk_name = "user"
    extra = 0


# ------------------- Custom User Admin -------------------
class CustomUserAdmin(SuperuserOnlyAdminMixin, DefaultUserAdmin):
    inlines = (UserBranchInline,)   # attach branch inline

    def branch(self, obj):
        """Show branch in user list page."""
        try:
            return obj.branch_assignment.branch.name if obj.branch_assignment and obj.branch_assignment.branch else "-"
        except Exception:
            return "-"
    branch.short_description = "Branch"

    # Show branch column in list_display
    list_display = DefaultUserAdmin.list_display + ("branch",)

    # Preserve all default filters and add branch filter
    list_filter = DefaultUserAdmin.list_filter + ("branch_assignment__branch",)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly += ['is_superuser', 'user_permissions', 'date_joined', 'last_login']
            if obj and obj.is_staff:
                readonly += ['groups']
        return readonly

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.is_superuser and not request.user.is_superuser:
            new_fieldsets = []
            for name, data in fieldsets:
                fields = tuple(f for f in data.get('fields', ()) if f != 'password')
                new_fieldsets.append((name, {'fields': fields}))
            return new_fieldsets
        if obj and not request.user.is_staff and request.user != obj:
            new_fieldsets = []
            for name, data in fieldsets:
                fields = tuple(f for f in data.get('fields', ()) if f != 'password')
                new_fieldsets.append((name, {'fields': fields}))
            return new_fieldsets
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.exclude(is_superuser=True)
        return qs


# ------------------- Register User & Group with Restrictions -------------------
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class CustomGroupAdmin(SuperuserOnlyAdminMixin, DefaultGroupAdmin):
    pass

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)