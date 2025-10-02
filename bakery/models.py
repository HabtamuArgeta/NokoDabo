from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Import centralized Branch model
from branches.models import Branch as BranchModel

class Bread(models.Model):
    name = models.CharField(max_length=100)
    weight = models.FloatField()        # in grams
    price = models.DecimalField(max_digits=8, decimal_places=2)
    baked_at = models.DateTimeField(auto_now_add=True)

class Injera(models.Model):
    batch_code = models.CharField(max_length=50)
    diameter = models.FloatField()      # in cm
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    fermented_days = models.IntegerField()

class WheatFlour(models.Model):
    supplier = models.CharField(max_length=100)
    package_size = models.FloatField()  # in kg
    stock_kg = models.FloatField()
    cost_per_kg = models.DecimalField(max_digits=8, decimal_places=2)

class Yeast(models.Model):
    brand = models.CharField(max_length=100)
    package_weight = models.FloatField() # in grams
    stock_units = models.IntegerField()

class Enhancer(models.Model):
    type = models.CharField(max_length=100)
    description = models.TextField()
    amount_used_per_batch = models.FloatField()

# -------- Inventory --------
class Inventory(models.Model):
    PRODUCT_CHOICES = [
        ('bread', 'Bread'),
        ('injera', 'Injera'),
        ('flour', 'Wheat Flour'),
        ('yeast', 'Yeast'),
        ('enhancer', 'Enhancer'),
    ]

    branch = models.ForeignKey(BranchModel, on_delete=models.CASCADE)  # <-- centralized branch
    product_type = models.CharField(max_length=20, choices=PRODUCT_CHOICES)
    product_id = models.PositiveIntegerField()  # Hidden, filled automatically
    product_name = models.CharField(max_length=100, blank=True)
    quantity = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} ({self.branch.name}) - {self.quantity}"


# -------- Stock Transaction --------
class StockTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
    )

    branch = models.ForeignKey(BranchModel, on_delete=models.CASCADE)  # <-- centralized branch
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
    product_id = models.PositiveIntegerField(null=True, blank=True)  # to link with actual product
    quantity = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.product_name} ({self.branch})"

    def save(self, *args, **kwargs):
        """Save transaction and update related inventory safely."""
        super().save(*args, **kwargs)

        from .models import Inventory

        inventory, created = Inventory.objects.get_or_create(
            branch=self.branch,
            product_type=self.product_type,
            product_name=self.product_name,
            defaults={'product_id': self.product_id or 0, 'quantity': 0}
        )

        if self.transaction_type == "in":
            inventory.quantity += self.quantity
        elif self.transaction_type == "out":
            # Validation is already handled in form.clean(), so this is always safe
            inventory.quantity -= self.quantity

        inventory.save()