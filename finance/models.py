# finance/models.py
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    )

    # Optional link to branch if you have branches app
    from branches.models import Branch  # local import for migrations/runtime
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, null=True, blank=True)

    product_type = models.CharField(max_length=50)   # bread, injera, flour, yeast, enhancer
    product_name = models.CharField(max_length=200, blank=True)
    quantity = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))  # price per unit or per kg
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    # optional source reference (e.g., stocktransaction id)
    source_app = models.CharField(max_length=100, blank=True, null=True)
    source_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product_type']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product_name} - {self.total_amount}"