from django.db import models

class Branch(models.Model):
    city = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.city})"