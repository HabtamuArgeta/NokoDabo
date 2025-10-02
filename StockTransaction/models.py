from django.db import models
from branches.models import Branch  # centralized branch

class StockTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
    )

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='stocktransaction_new_set')  # centralized branch
    product_type = models.CharField(
        max_length=20,
        choices=[
            ("bread", "Bread"),
            ("injera", "Injera"),
            ("flour", "Wheat Flour"),
            ("yeast", "Yeast"),
            ("enhancer", "Enhancer"),
        ]
    )
    product_name = models.CharField(max_length=100)
    product_id = models.PositiveIntegerField(null=True, blank=True)
    quantity = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.product_name} ({self.branch})"

    def save(self, *args, **kwargs):
        """Save transaction and update related inventory safely."""
        super().save(*args, **kwargs)

        from bakery.models import Inventory  # Inventory still in bakery

        inventory, created = Inventory.objects.get_or_create(
            branch=self.branch,
            product_type=self.product_type,
            product_name=self.product_name,
            defaults={'product_id': self.product_id or 0, 'quantity': 0}
        )

        if self.transaction_type == "in":
            inventory.quantity += self.quantity
        elif self.transaction_type == "out":
            inventory.quantity -= self.quantity

        inventory.save()