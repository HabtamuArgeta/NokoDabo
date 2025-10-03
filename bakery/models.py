from django.db import models
from branches.models import Branch as BranchModel

# ------------------- Bakery Products -------------------
class Bread(models.Model):
    name = models.CharField(max_length=100)
    flour_kg = models.FloatField()  # flour in kg
    yeast_kg = models.FloatField()  # yeast in kg
    enhancer_kg = models.FloatField()  # enhancer in kg
    water_birr = models.DecimalField(max_digits=8, decimal_places=2)  # water cost
    electricity_birr = models.DecimalField(max_digits=8, decimal_places=2)  # electricity cost
    selling_price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Injera(models.Model):
    name = models.CharField(max_length=100)
    flour_kg = models.FloatField()  # flour in kg
    yeast_kg = models.FloatField()  # yeast in kg
    water_birr = models.DecimalField(max_digits=8, decimal_places=2)  # water cost
    electricity_birr = models.DecimalField(max_digits=8, decimal_places=2)  # electricity cost
    selling_price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Enhancer(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    cost_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Yeast(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    cost_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Flour(models.Model):  # Renamed from WheatFlour
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    cost_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ------------------- Inventory -------------------
class Inventory(models.Model):
    PRODUCT_CHOICES = [
        ('bread', 'Bread'),
        ('injera', 'Injera'),
        ('flour', 'Flour'),      # updated from Wheat Flour
        ('yeast', 'Yeast'),
        ('enhancer', 'Enhancer'),
    ]

    branch = models.ForeignKey(BranchModel, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=20, choices=PRODUCT_CHOICES)
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=100, blank=True)
    quantity = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} ({self.branch.name}) - {self.quantity}"