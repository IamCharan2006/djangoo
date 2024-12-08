from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # Order URLs
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('order/<int:order_id>/track/', views.track_order, name='track_order'),
    
    # Order History URLs
    path('history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/reorder/', views.reorder, name='reorder'),
    
    # Rating URLs
    path('order/<int:order_id>/rate/', views.rate_order, name='rate_order'),
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('order_success/', views.order_success, name='order_success'),
    path('order_failed/', views.order_failed, name='order_failed'),
    path('paypal_payment',views.paypal_payment,name='paypal_payment'),
] 