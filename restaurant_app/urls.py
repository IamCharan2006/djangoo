from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('dashboard/', views.restaurant_dashboard, name='dashboard'),
    path('add-menu-item/', views.add_menu_item, name='add_menu_item'),
    path('register/', views.register_restaurant, name='register'),
    path('menu/categories/', views.manage_menu_categories, name='manage_menu_categories'),
    path('menu/categories/<int:category_id>/items/', views.manage_category_items, name='manage_category_items'),
    path('menu/manage/<int:restaurant_id>/', views.restaurant_menu_management, name='menu_management'),
    path('restaurant/<int:restaurant_id>/menu/', views.restaurant_menu_view, name='menu_view'),
    path('edit-menu-item/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('toggle-menu-item/<int:item_id>/', views.toggle_menu_item, name='toggle_menu_item'),
    path('delete-menu-item/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='detail'),

]
