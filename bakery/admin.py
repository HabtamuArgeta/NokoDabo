from django.contrib import admin
from .forms import InventoryForm, StockTransactionForm
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin, GroupAdmin as DefaultGroupAdmin
from django.contrib.auth.models import User, Group
from .models import Bread, Injera, WheatFlour, Yeast, Enhancer, Branch, Inventory, StockTransaction

# ------------------- Bakery Models -------------------
@admin.register(Bread)
class BreadAdmin(admin.ModelAdmin):
    list_display = ("name", "weight", "price", "baked_at")
    search_fields = ("name",)
    list_filter = ("baked_at",)


@admin.register(Injera)
class InjeraAdmin(admin.ModelAdmin):
    list_display = ("batch_code", "diameter", "quantity", "price", "fermented_days")
    search_fields = ("batch_code",)
    list_filter = ("fermented_days",)


@admin.register(WheatFlour)
class WheatFlourAdmin(admin.ModelAdmin):
    list_display = ("supplier", "package_size", "stock_kg", "cost_per_kg")
    search_fields = ("supplier",)
    list_filter = ("supplier",)


@admin.register(Yeast)
class YeastAdmin(admin.ModelAdmin):
    list_display = ("brand", "package_weight", "stock_units")
    search_fields = ("brand",)


@admin.register(Enhancer)
class EnhancerAdmin(admin.ModelAdmin):
    list_display = ("type", "description", "amount_used_per_batch")
    search_fields = ("type",)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at')
    search_fields = ('name', 'location')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    form = InventoryForm
    list_display = ('branch', 'product_type', 'product_name', 'quantity', 'last_updated')
    list_filter = ('branch', 'product_type', 'product_name')
    search_fields = ('product_name', )

    class Media:
        js = ('bakery/js/inventory.js',)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    form = StockTransactionForm
    list_display = ('branch', 'product_type', 'product_name', 'transaction_type', 'quantity', 'created_at')
    list_filter = ('branch', 'product_type', 'transaction_type')
    search_fields = ('product_name',)

    class Media:
        js = ("bakery/js/stocktransaction.js",)


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


# ------------------- Custom User Admin -------------------
class CustomUserAdmin(SuperuserOnlyAdminMixin, DefaultUserAdmin):
    # Keep your existing functionality intact
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


# ------------------- Register User & Group with restrictions -------------------
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Only superusers can access Groups
class CustomGroupAdmin(SuperuserOnlyAdminMixin, DefaultGroupAdmin):
    pass

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
