# branches/models.py
from django.db import models
from django.contrib.auth.models import User

class Branch(models.Model):
    city = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.city})"


class UserBranch(models.Model):
    # one-to-one to user; branch can be null/blank so existing users don't break
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="branch_assignment")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, related_name="assigned_users")

    def __str__(self):
        branch_name = self.branch.name if self.branch else "No Branch"
        return f"{self.user.username} → {branch_name}"