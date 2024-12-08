from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from restaurant_app.models import Restaurant, MenuItem, Order, MenuCategory
from auth_app.models import UserProfile, RestaurantProfile
from auth_app.forms import UserRegisterForm
from .forms import RestaurantRegistrationForm, MenuCategoryForm, MenuItemForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from user_app.models import Favorite

@login_required
def restaurant_dashboard(request):
    if hasattr(request.user, 'restaurantprofile'):
        restaurant = request.user.restaurantprofile.restaurant
        today = timezone.now().date()
        
        # Get statistics
        today_orders = Order.objects.filter(
            restaurant=restaurant,
            created_at__date=today
        )
        
        yesterday_orders = Order.objects.filter(
            restaurant=restaurant,
            created_at__date=today - timedelta(days=1)
        )

        # Calculate differences for trends
        today_orders_count = today_orders.count()
        yesterday_orders_count = yesterday_orders.count()
        orders_difference = today_orders_count - yesterday_orders_count

        today_revenue = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        yesterday_revenue = yesterday_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        revenue_difference = today_revenue - yesterday_revenue

        # Get popular items using the correct related name
        popular_items = MenuItem.objects.filter(restaurant=restaurant)\
            .annotate(order_count=Count('restaurant_order_items'))\
            .order_by('-order_count')[:5]

        context = {
            'restaurant': restaurant,
            'stats': {
                'today_orders': today_orders_count,
                'yesterday_orders': yesterday_orders_count,
                'orders_difference': orders_difference,
                'today_revenue': today_revenue,
                'yesterday_revenue': yesterday_revenue,
                'revenue_difference': revenue_difference,
                'rating': restaurant.rating,
                'active_orders': today_orders.filter(status__in=['pending', 'preparing']).count(),
            },
            'recent_orders': Order.objects.filter(restaurant=restaurant)\
                                        .order_by('-created_at')[:5],
            'popular_items': popular_items,
            'menu_items': MenuItem.objects.filter(restaurant=restaurant)\
                                        .order_by('-is_available', 'name'),
        }
        return render(request, 'restaurant_app/Restaurant_DashBoard.html', context)
    else:
        messages.error(request, "Restaurant profile not found.")
        return redirect('HomePage')

@login_required
def add_menu_item(request, item_id=None):
    restaurant = request.user.restaurantprofile.restaurant
    menu_item = None
    if item_id:
        menu_item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.main_category = form.cleaned_data['main_category']
            menu_item.sub_category = form.cleaned_data['sub_category']
            menu_item.save()
            messages.success(request, f'Menu item {"updated" if item_id else "added"} successfully!')
            return redirect('restaurant:menu_management', restaurant_id=restaurant.id)
    else:
        initial_data = {}
        if menu_item:
            initial_data = {
                'name': menu_item.name,
                'description': menu_item.description,
                'price': menu_item.price,
                'main_category': menu_item.main_category,
                'sub_category': menu_item.sub_category,
                'is_available': menu_item.is_available,
            }
        form = MenuItemForm(instance=menu_item, initial=initial_data)
    
    context = {
        'form': form,
        'menu_item': menu_item,
        'is_edit': bool(item_id)
    }
    return render(request, 'restaurant_app/add_menu_item.html', context)

@login_required
def register_restaurant(request):
    if request.method == 'POST':
        form = RestaurantRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.save()
            
            # Create RestaurantProfile
            RestaurantProfile.objects.create(
                user=request.user,
                restaurant=restaurant,
                role='restaurant'
            )
            
            # Create default menu categories
            default_categories = ['Starters', 'Main Course', 'Desserts', 'Beverages']
            for idx, cat_name in enumerate(default_categories):
                MenuCategory.objects.create(
                    restaurant=restaurant,
                    name=cat_name,
                    order=idx
                )
            
            messages.success(request, 'Restaurant registered successfully!')
            return redirect('restaurant:dashboard')
    else:
        form = RestaurantRegistrationForm()
    
    return render(request, 'restaurant_app/register_restaurant.html', {'form': form})

@login_required
def manage_menu_categories(request):
    restaurant = request.user.restaurantprofile.restaurant
    categories = MenuCategory.objects.filter(restaurant=restaurant)
    
    if request.method == 'POST':
        form = MenuCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.restaurant = restaurant
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('restaurant:manage_menu_categories')
    else:
        form = MenuCategoryForm()
        
    context = {
        'categories': categories,
        'form': form
    }
    return render(request, 'restaurant_app/manage_menu_categories.html', context)

@login_required
def manage_category_items(request, category_id):
    restaurant = request.user.restaurantprofile.restaurant
    category = get_object_or_404(MenuCategory, id=category_id, restaurant=restaurant)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.category = category
            menu_item.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('restaurant:manage_category_items', category_id=category_id)
    else:
        form = MenuItemForm()
    
    items = MenuItem.objects.filter(category=category)
    context = {
        'category': category,
        'items': items,
        'form': form
    }
    return render(request, 'restaurant_app/manage_category_items.html', context)

@login_required
def restaurant_menu_management(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.user.restaurantprofile.restaurant != restaurant:
        messages.error(request, "You don't have permission to manage this restaurant's menu")
        return redirect('restaurant:dashboard')
    
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    main_categories_dict = dict(MenuItemForm.MAIN_CATEGORIES[1:])  # Skip the empty choice
    
    # Create a dictionary of items grouped by display names
    categorized_items = {}
    for item in menu_items:
        category_display_name = main_categories_dict.get(item.main_category, item.main_category)
        if category_display_name not in categorized_items:
            categorized_items[category_display_name] = []
        categorized_items[category_display_name].append(item)
    
    context = {
        'restaurant': restaurant,
        'categorized_items': categorized_items,
    }
    return render(request, 'restaurant_app/menu_management.html', context)

def restaurant_menu_view(request, restaurant_id):
    """View for customers to see restaurant menu and order"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = MenuItem.objects.filter(
        restaurant=restaurant,
        is_available=True
    ).order_by('category')
    
    context = {
        'restaurant': restaurant,
        'menu_items': menu_items,
    }
    return render(request, 'restaurant_app/restaurant_menu.html', context)

@login_required
def edit_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    restaurant = request.user.restaurantprofile.restaurant
    
    # Check if user has permission to edit this item
    if menu_item.restaurant != restaurant:
        messages.error(request, "You don't have permission to edit this menu item")
        return redirect('restaurant:dashboard')
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.main_category = form.cleaned_data['main_category']
            menu_item.sub_category = form.cleaned_data['sub_category']
            menu_item.save()
            messages.success(request, 'Menu item updated successfully!')
            return redirect('restaurant:menu_management', restaurant_id=restaurant.id)
    else:
        form = MenuItemForm(instance=menu_item, initial={
            'main_category': menu_item.main_category,
            'sub_category': menu_item.sub_category
        })
    
    context = {
        'form': form,
        'menu_item': menu_item,
        'is_edit': True
    }
    return render(request, 'restaurant_app/add_menu_item.html', context)

@login_required
@require_POST
def toggle_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    restaurant = request.user.restaurantprofile.restaurant
    
    if menu_item.restaurant != restaurant:
        return JsonResponse({
            'success': False,
            'message': "You don't have permission to modify this menu item"
        }, status=403)
    
    menu_item.is_available = not menu_item.is_available
    menu_item.save()
    
    return JsonResponse({
        'success': True,
        'is_available': menu_item.is_available,
        'message': f'Item is now {"available" if menu_item.is_available else "unavailable"}'
    })

@login_required
@require_POST
def delete_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    restaurant = request.user.restaurantprofile.restaurant
    
    if menu_item.restaurant != restaurant:
        return JsonResponse({
            'success': False,
            'message': "You don't have permission to delete this menu item"
        }, status=403)
    
    menu_item.delete()
    return JsonResponse({
        'success': True,
        'message': 'Menu item deleted successfully'
    })

@login_required
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Get all menu items and organize by category
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    categorized_items = {}
    
    for item in menu_items:
        if item.main_category not in categorized_items:
            categorized_items[item.main_category] = []
        categorized_items[item.main_category].append(item)
    
    # Get user's favorites
    user_favorites = set()
    if request.user.is_authenticated:
        user_favorites = set(
            Favorite.objects.filter(
                user=request.user,
                menu_item__in=menu_items
            ).values_list('menu_item_id', flat=True)
        )
    
    context = {
        'restaurant': restaurant,
        'categorized_items': categorized_items,
        'user_favorites': user_favorites,
    }
    
    return render(request, 'restaurant_app/restaurant_detail.html', context)

def home(request):
    # Regular homepage content
    featured_restaurants = Restaurant.objects.filter(is_featured=True)
    categories = MenuCategory.objects.all()
    
    context = {
        'featured_restaurants': featured_restaurants,
        'categories': categories,
    }
    
    # Add user-specific content if logged in
    if request.user.is_authenticated:
        try:
            recent_orders = Order.objects.filter(
                customer=request.user
            ).order_by('-created_at')[:5]
        except:
            recent_orders = []
            
        try:
            favorite_items = Favorite.objects.filter(
                user=request.user
            ).select_related('menu_item')[:6]
        except:
            favorite_items = []
            
        context.update({
            'recent_orders': recent_orders,
            'favorite_items': favorite_items,
            'is_authenticated': True
        })
    
    return render(request, 'ProjectHomePage.html', context)