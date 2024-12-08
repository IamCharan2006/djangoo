from django.contrib import admin
from .models import RestaurantProfile, UserProfile, Profile

admin.site.register(RestaurantProfile)
admin.site.register(UserProfile)
admin.site.register(Profile)
