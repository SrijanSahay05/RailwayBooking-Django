from django.contrib import admin
from .models import CustomUser, CustomerProfile, RailwayStaffProfile

admin.site.register(CustomUser)
admin.site.register(CustomerProfile)
admin.site.register(RailwayStaffProfile)
