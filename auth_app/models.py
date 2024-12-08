from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class RestaurantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant = models.OneToOneField('restaurant_app.Restaurant', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, default='restaurant')
    restaurant_image = models.ImageField(upload_to='restaurant_images/', default='defaults/default_restaurant.jpg')
    restaurant_banner = models.ImageField(upload_to='restaurant_banners/', default='defaults/default_banner.jpg')

    def __str__(self):
        return f"{self.user.username} - Restaurant Profile"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, default='user')

    def __str__(self):
        return f"{self.user.username} - User Profile"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Get or create profile for existing users
        Profile.objects.get_or_create(user=instance)
