from django.core.management.base import BaseCommand
from restaurant_app.models import Restaurant
from django.core.files import File
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Creates sample restaurant data'

    def handle(self, *args, **kwargs):
        restaurants_data = [
            {
                'name': 'Pizza Palace',
                'description': 'Best pizza in town',
                'address': '123 Food Street',
                'phone': '+1234567890',
                'email': 'pizza@example.com',
                'cuisine_types': 'Italian, Pizza',
                'opening_time': '10:00',
                'closing_time': '22:00',
                'delivery_radius': 5.0,
                'minimum_order': 200.00,
                'delivery_fee': 0.00,
                'rating': 4.8,
                # Image will use default if not specified
            },
            # Add more restaurants as needed
        ]

        for data in restaurants_data:
            Restaurant.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample restaurants')) 