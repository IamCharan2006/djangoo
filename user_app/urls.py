from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('restaurants/', views.restaurants_view, name='restaurants'),
    path('orders/', views.orders_list, name='orders'),
    path('user_dashboard/', views.user_dashboard, name='dashboard'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('profile/', views.user_profile, name='profile'),
    path('settings/', views.user_settings, name='settings'),
    path('toggle-favorite/<int:item_id>/', views.toggle_favorite, name='toggle_favorite'),
]
