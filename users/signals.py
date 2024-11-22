from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CustomerProfile, RailwayStaffProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == "customer":
            CustomerProfile.objects.create(user=instance)
        if instance.user_type == "railway_staff":
            RailwayStaffProfile.objects.create(user=instance)
