from django.contrib import admin
from .forms import StockTransactionForm
from .models import StockTransaction

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    form = StockTransactionForm
    list_display = ('branch', 'product_type', 'product_name', 'transaction_type', 'quantity', 'created_at')
    list_filter = ('branch', 'product_type', 'transaction_type')
    search_fields = ('product_name',)

    class Media:
        js = ("StockTransaction/js/stocktransaction.js",)