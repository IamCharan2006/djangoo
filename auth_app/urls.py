from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'auth'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('restaurant/register/', views.register_restaurant, name='register_restaurant'),
]