from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count

# class RestaurantCategory(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to='restaurant_categories/', blank=True)
#     
#     def __str__(self):
#         return self.name

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    delivery_radius = models.DecimalField(max_digits=5, decimal_places=2)  # in km
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    total_ratings = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to='restaurant_images/',
        default='defaults/default_restaurant.jpg'
    )
    banner = models.ImageField(upload_to='restaurant_banners/', default='defaults/default_banner.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # category = models.ForeignKey(RestaurantCategory, on_delete=models.SET_NULL, null=True, blank=True)
    specialties = models.TextField(blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    preparation_time = models.IntegerField(default=30)
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='restaurant_docs/', blank=True)

    def __str__(self):
        return self.name
    @property
    def average_rating(self):
        if self.total_ratings > 0:
            return self.rating / self.total_ratings
        return 0.0

    @property
    def is_open(self):
        current_time = timezone.now().time()
        return self.opening_time <= current_time <= self.closing_time

    @property
    def formatted_delivery_time(self):
        """Returns delivery time in a user-friendly format"""
        if self.delivery_time < 30:
            return f"{self.delivery_time} mins"
        hours = self.delivery_time // 60
        mins = self.delivery_time % 60
        return f"{hours}h {mins}m" if mins else f"{hours}h"

    @property
    def rating_display(self):
        """Returns rating with star display"""
        return "★" * int(self.average_rating()) + "☆" * (5 - int(self.average_rating()))

    def get_popular_items(self):
        """Returns most ordered menu items"""
        return self.menu_items.annotate(
            order_count=Count('restaurant_order_items')
        ).order_by('-order_count')[:5]

class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='menu_categories/', blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Menu Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/')
    main_category = models.CharField(max_length=100, default='main_course')
    sub_category = models.CharField(max_length=100, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurant_orders')
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.restaurant.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='restaurant_order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

