# branches/signals.py
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserBranch

@receiver(post_save, sender=User)
def ensure_userbranch(sender, instance, created, **kwargs):
    if created:
        # create an empty assignment row so admin inline exists
        UserBranch.objects.create(user=instance, branch=None)