from django.core.management.base import BaseCommand
from auth_app.models import RestaurantProfile
from restaurant_app.models import Restaurant

class Command(BaseCommand):
    help = 'Links RestaurantProfiles with Restaurants'

    def handle(self, *args, **kwargs):
        for profile in RestaurantProfile.objects.filter(restaurant__isnull=True):
            restaurant = Restaurant.objects.create(
                name=f"{profile.user.username}'s Restaurant",
                description='Restaurant description',
                address='Address pending',
                phone='Phone pending',
                email=profile.user.email,
                cuisine_types='Various',
                opening_time='09:00',
                closing_time='22:00',
                delivery_radius=5.0,
                minimum_order=0.0,
                delivery_fee=0.0,
            )
            profile.restaurant = restaurant
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'Created restaurant for {profile.user.username}')) 