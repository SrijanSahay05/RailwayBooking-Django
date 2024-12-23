from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("cutomer", "Customer"),
        ("railway_taff", "Railway Staff"),
        ("superadmin", "Super Admin"),
    )
    user_type = models.CharField(
        choices=USER_TYPE_CHOICES, max_length=255, default="customer"
    )
    # USERNAME_FIELD = "email"


class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class RailwayStaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
