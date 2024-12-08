from django.shortcuts import render
from restaurant_app.models import Restaurant

def homepage(request):
    restaurants = Restaurant.objects.all()[:8]  # Get first 8 restaurants
    context = {
        'restaurants': restaurants,
    }
    return render(request, 'ProjectHomePage.html', context) 