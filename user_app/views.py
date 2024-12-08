from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from restaurant_app.models import MenuItem, Order, Restaurant
from auth_app.models import RestaurantProfile
from .models import Favorite
from django.db.models import Q
from django.http import JsonResponse
from user_app.models import Favorite


@login_required
def user_dashboard(request):
    # Get recent orders
    recent_orders = Order.objects.filter(
        customer=request.user
    ).order_by('-created_at')[:5]

    # Get favorite items
    favorite_items = Favorite.objects.filter(
        user=request.user
    ).select_related('menu_item')[:6]

    # Get top restaurants with prefetch_related for optimization
    top_restaurants = Restaurant.objects.all().prefetch_related(
        'menuitem_set'
    ).order_by('-rating')[:6]

    context = {
        'user': request.user,
        'recent_orders': recent_orders,
        'favorite_items': favorite_items,
        'top_restaurants': top_restaurants,
        'is_dashboard': True  # Add this flag
    }
    return render(request, 'user_app/User_DashBoard.html', context)


@login_required
def restaurants_list(request):
    restaurants = RestaurantProfile.objects.all()
    context = {'restaurants': restaurants}
    return render(request, 'user_app/restaurants.html', context)


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('menu_item')
    context = {'favorites': favorites}
    return render(request, 'user_app/favorites.html', context)


@login_required
def orders_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'user_app/orders.html', context)


@login_required
def user_profile(request):
    if request.method == 'POST':
        # Handle profile update logic here
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    context = {
        'user': request.user,
        'profile': request.user.userprofile
    }
    return render(request, 'user_app/profile.html', context)


@login_required
def user_settings(request):
    if request.method == 'POST':
        # Handle settings update logic here
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')

    context = {
        'user': request.user
    }
    return render(request, 'user_app/settings.html', context)


@login_required
def restaurants_view(request):
    restaurants = Restaurant.objects.all()
    print(f"Total restaurants found: {restaurants.count()}")
    print(f"First restaurant: {restaurants.first() if restaurants.exists() else 'None'}")

    # Get unique cuisines for the filter dropdown
    cuisines = Restaurant.objects.values_list('specialties', flat=True).distinct()

    # Handle filters
    current_filters = {
        'search': request.GET.get('search', ''),
        'cuisine': request.GET.get('cuisine', ''),
        'sort': request.GET.get('sort', '')
    }

    # Apply filters
    if current_filters['search']:
        restaurants = restaurants.filter(
            Q(name__icontains=current_filters['search']) |
            Q(specialties__icontains=current_filters['search'])
        )

    if current_filters['cuisine']:
        restaurants = restaurants.filter(specialties__icontains=current_filters['cuisine'])

    if current_filters['sort'] == 'rating':
        restaurants = restaurants.order_by('-rating')
    elif current_filters['sort'] == 'delivery_time':
        restaurants = restaurants.order_by('preparation_time')

    context = {
        'restaurants': restaurants,
        'cuisines': cuisines,
        'current_filters': current_filters
    }

    return render(request, 'user_app/restaurants.html', context)


@login_required
def toggle_favorite(request, item_id):
    try:
        menu_item = MenuItem.objects.get(id=item_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            menu_item=menu_item
        )

        if not created:
            favorite.delete()
            is_favorite = False
            message = f"Removed {menu_item.name} from favorites"
        else:
            is_favorite = True
            message = f"Added {menu_item.name} to favorites"

        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })

    except MenuItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Menu item not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)

    # Get user's favorites if logged in
    user_favorites = set()
    if request.user.is_authenticated:
        user_favorites = set(
            Favorite.objects.filter(
                user=request.user,
                menu_item__in=menu_items
            ).values_list('menu_item_id', flat=True)
        )

    # Group menu items by category
    categorized_items = {}
    for item in menu_items:
        category = item.main_category or 'Other'
        if category not in categorized_items:
            categorized_items[category] = []
        categorized_items[category].append(item)

    context = {
        'restaurant': restaurant,
        'categorized_items': categorized_items,
        'user_favorites': user_favorites  # Add this to the context
    }

    return render(request, 'restaurant_app/restaurant_detail.html', context)



