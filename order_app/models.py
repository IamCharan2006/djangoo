from django.db import models
from django.contrib.auth.models import User
from restaurant_app.models import MenuItem
import uuid
from django.core.mail import send_mail
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return sum(item.get_total() for item in self.cartitem_set.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return self.menu_item.price * self.quantity

    class Meta:
        unique_together = ('cart', 'menu_item')

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    delivery_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            old_status = Order.objects.get(pk=self.pk).status
            
        super().save(*args, **kwargs)
        
        if is_new or old_status != self.status:
            self.send_status_notification()
            self.send_websocket_update()

    def send_status_notification(self):
        subject = f'Order #{self.order_number} Status Update'
        context = {
            'order': self,
            'status': dict(self.STATUS_CHOICES)[self.status]
        }
        html_message = render_to_string('order_app/email/status_update.html', context)
        
        send_mail(
            subject=subject,
            message='',
            html_message=html_message,
            from_email='noreply@foodieexpress.com',
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def send_websocket_update(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'order_{self.id}',
            {
                'type': 'order_status_update',
                'status': self.status,
                'timestamp': self.updated_at.strftime('%I:%M %p')
            }
        )

    def get_subtotal(self):
        return self.total_amount - self.delivery_fee

    def get_total(self):
        return self.total_amount

    def __str__(self):
        return f"Order #{self.order_number}"

    def has_rating(self):
        return hasattr(self, 'rating')

    def get_rating(self):
        return self.rating if self.has_rating() else None

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='customer_order_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return self.menu_item.price * self.quantity

    class Meta:
        unique_together = ('order', 'menu_item')

class OrderRating(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='rating')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating for Order #{self.order.order_number}"
