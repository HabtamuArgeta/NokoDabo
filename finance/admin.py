# finance/admin.py
from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'branch', 'product_type', 'product_name', 'quantity', 'unit_price', 'total_amount', 'transaction_type')
    list_filter = ('transaction_type', 'product_type', 'created_at', 'branch')
    search_fields = ('product_name', 'product_type', 'source_app', 'source_id')
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = ['created_at', 'branch', 'product_type', 'product_name', 'quantity', 'unit_price', 'total_amount', 'transaction_type', 'source_app', 'source_id']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=transactions.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = [
                getattr(obj, 'created_at'),
                getattr(obj.branch, 'name', '') if obj.branch else '',
                obj.product_type,
                obj.product_name,
                obj.quantity,
                obj.unit_price,
                obj.total_amount,
                obj.transaction_type,
                obj.source_app,
                obj.source_id,
            ]
            writer.writerow(row)
        return response
    export_as_csv.short_description = "Export selected transactions to CSV"