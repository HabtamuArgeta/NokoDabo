from django.contrib import admin
from .forms import InventoryForm, StockTransactionForm
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from .models import Bread, Injera, WheatFlour, Yeast, Enhancer, Branch, Inventory, StockTransaction


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
    list_filter = ('branch', 'product_type','product_name')
    search_fields = ('product_name', )

    class Media:
        # path relative to STATICFILES — we put file in bakery/static/bakery/js/inventory.js
        js = ('bakery/js/inventory.js',)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    form = StockTransactionForm
    list_display = ('branch', 'product_type', 'product_name', 'transaction_type', 'quantity', 'created_at')
    list_filter = ('branch', 'product_type', 'transaction_type')
    search_fields = ('product_name',)

    class Media:
        js = ("bakery/js/stocktransaction.js",)


# ---- Custom User admin ----
class CustomUserAdmin(DefaultUserAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        # Make superuser-related fields read-only for non-superusers
        if not request.user.is_superuser:
            readonly += ['is_superuser', 'user_permissions']

            # Make join/login date read-only for staff & ordinary users
            readonly += ['date_joined', 'last_login']

            # 🚫 If editing a staff user, prevent editing groups
            if obj and obj.is_staff:
                readonly += ['groups']

            # ✅ Otherwise (ordinary users), staff can edit groups

        return readonly

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        # If editing a superuser and current user is not a superuser → remove password field
        if obj and obj.is_superuser and not request.user.is_superuser:
            new_fieldsets = []
            for name, data in fieldsets:
                fields = tuple(f for f in data.get('fields', ()) if f != 'password')
                new_fieldsets.append((name, {'fields': fields}))
            return new_fieldsets

        # If current user is NOT staff and tries to edit someone else → remove password
        if obj and not request.user.is_staff and request.user != obj:
            new_fieldsets = []
            for name, data in fieldsets:
                fields = tuple(f for f in data.get('fields', ()) if f != 'password')
                new_fieldsets.append((name, {'fields': fields}))
            return new_fieldsets

        return fieldsets

    def get_queryset(self, request):
        """Control which users appear in the list"""
        qs = super().get_queryset(request)

        # ✅ Hide superusers from staff & ordinary users
        if not request.user.is_superuser:
            return qs.exclude(is_superuser=True)

        return qs


# Unregister default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
