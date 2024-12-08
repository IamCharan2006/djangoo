from django.conf import settings

def default_images(request):
    return {
        'DEFAULT_RESTAURANT_IMAGE': 'images/defaults/default_restaurant.jpg',
        'DEFAULT_BANNER_IMAGE': 'images/defaults/default_banner.jpg',
    } 