from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
import csv
from .models import Transaction
from . import views

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # Add product_type to list_display
    list_display = (
        "created_at",
        "transaction_type",
        "product_type",
        "product_name",
        "quantity",
        "unit_price",
        "total_amount"
    )
    
    # Enable filtering by transaction_type and product_type
    list_filter = (
        "transaction_type",
        "product_type",
        "product_name",
        "created_at"
    )

    actions = ["export_as_csv"]

    # Custom admin URLs for graph only (PDF removed)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "report/graph/",
                self.admin_site.admin_view(views.finance_graph),
                name="finance_report_graph"
            ),
        ]
        return custom_urls + urls

    # Add buttons to changelist page (PDF button removed)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["extra_buttons"] = [
            {"url": "report/graph/", "label": "📊 View Finance Graph"},
        ]
        return super().changelist_view(request, extra_context=extra_context)

    # CSV Export Action
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=finance_report.csv"
        writer = csv.writer(response)
        writer.writerow([
            "Created At",
            "Transaction Type",
            "Product Type",
            "Product Name",
            "Quantity",
            "Unit Price",
            "Total Amount"
        ])
        for obj in queryset:
            writer.writerow([
                obj.created_at,
                obj.transaction_type,
                obj.product_type,
                obj.product_name,
                obj.quantity,
                obj.unit_price,
                obj.total_amount
            ])
        return response

    export_as_csv.short_description = "Export Selected as CSV"