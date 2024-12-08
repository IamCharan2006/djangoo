from django.contrib.auth.models import User
from auth_app.models import Profile

# Create profiles for users that don't have one
for user in User.objects.all():
    Profile.objects.get_or_create(user=user) 