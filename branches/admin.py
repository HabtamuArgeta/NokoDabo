from django.contrib import admin
from .models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "address", "created_at")
    search_fields = ("name", "city")
    list_filter = ("city",)