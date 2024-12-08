from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Cart, CartItem, Order, OrderItem
from .forms import OrderRatingForm
from django.http import JsonResponse
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from restaurant_app.models import OrderItem
from django.contrib.auth.decorators import login_required
from .utils import razorpay_client

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {'cart': cart}
    return render(request, 'order_app/cart.html', context)

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        menu_item_id = request.POST.get('menu_item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{menu_item.name} added to cart')
        return redirect(request.META.get('HTTP_REFERER', reverse('order:cart')))
    
    return redirect('order:cart')

@login_required
def update_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Quantity updated')
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, 'Quantity updated')
            else:
                cart_item.delete()
                messages.success(request, 'Item removed from cart')
        
    return redirect('order:cart')

@login_required
def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
    
    return redirect('order:cart')
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta
import razorpay

from .models import Order, OrderItem, Cart, CartItem
from .forms import OrderRatingForm
from django.conf import settings

# Razorpay client setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from order_app.models import Cart, Order

@login_required
def checkout(request):
    if request.method == 'POST':
        # Get the latest cart for the user
        cart = Cart.objects.filter(user=request.user).last()

        # Check if the cart exists
        if not cart:
            messages.error(request, 'Your cart is empty or no active cart found.')
            return redirect('order:cart')

        # Check if the cart has items
        if not cart.cartitem_set.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('order:cart')

        # Create the order (example structure)
        order = Order.objects.create(user=request.user)
        for cart_item in cart.cartitem_set.all():
            order.orderitem_set.create(
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )

        # Clear the cart after checkout
        cart.delete()
        messages.success(request, 'Order placed successfully!')
        return redirect('order:confirmation')

    return redirect('order:cart')

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_app/order_confirmation.html', {'order': order})


@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_app/track_order.html', {'order': order})


@login_required
def order_history(request):
    status = request.GET.get('status', '')
    date_range = request.GET.get('date_range', '')
    sort_by = request.GET.get('sort_by', '-created_at')
    search = request.GET.get('search', '')

    orders = Order.objects.filter(user=request.user)

    if status:
        orders = orders.filter(status=status)
    if date_range:
        if date_range == 'today':
            orders = orders.filter(created_at__date=timezone.now().date())
        elif date_range == 'week':
            orders = orders.filter(created_at__gte=timezone.now() - timedelta(days=7))
        elif date_range == 'month':
            orders = orders.filter(created_at__gte=timezone.now() - timedelta(days=30))
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(items__menu_item__name__icontains=search)
        ).distinct()

    orders = orders.order_by(sort_by)
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    context = {
        'orders': orders,
        'current_filters': {
            'status': status,
            'date_range': date_range,
            'sort_by': sort_by,
            'search': search
        },
        'status_choices': Order.STATUS_CHOICES
    }
    return render(request, 'order_app/order_history.html', context)


@login_required
def reorder(request, order_id):
    if request.method == 'POST':
        original_order = get_object_or_404(Order, id=order_id, user=request.user)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Clear existing cart and add items from original order
        cart.cartitem_set.all().delete()
        for item in original_order.items.all():
            CartItem.objects.create(
                cart=cart,
                menu_item=item.menu_item,
                quantity=item.quantity
            )
        messages.success(request, 'Items added to cart!')
        return redirect('order:cart')

    return redirect('order:order_history')


@login_required
def rate_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        form = OrderRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.order = order
            rating.save()
            messages.success(request, 'Thank you for your feedback!')
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

    form = OrderRatingForm()
    return render(request, 'order_app/rating_modal.html', {'form': form, 'order': order})


@login_required
def initiate_payment(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(cart__user=request.user)

        if not cart_items:
            return redirect('user_app:cart')

        cart_total = sum(item.quantity * item.menu_item.price for item in cart_items)
        amount_in_paise = int(cart_total * 100)

        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1'
        })

        order = Order.objects.create(
            user=request.user,
            razorpay_order_id=razorpay_order['id'],
            total_amount=cart_total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                quantity=item.quantity,
                price=item.menu_item.price
            )

        context = {
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order_id': razorpay_order['id'],
            'amount': cart_total,
            'amount_in_paise': amount_in_paise,
            'order': order
        }
        return render(request, 'order_app/payment.html', context)

    return redirect('user_app:cart')


@login_required
def payment_callback(request):
    if request.method == 'POST':
        payment_data = request.POST
        razorpay_order_id = payment_data.get('razorpay_order_id')
        razorpay_payment_id = payment_data.get('razorpay_payment_id')

        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.payment_id = razorpay_payment_id
            order.status = 'Paid'
            order.save()

            CartItem.objects.filter(cart__user=request.user).delete()

            return redirect('order:order_success')
        except Exception as e:
            print(f"Error: {e}")
            return redirect('order:order_failed')

    return redirect('user_app:cart')


@login_required
def order_success(request):
    return render(request, 'order_app/order_success.html')


@login_required
def order_failed(request):
    return render(request, 'order_app/order_failed.html')

# import razorpay
# from django.conf import settings
#
# # Razorpay client initialization
# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def paypal_payment(request):
    return render(request, 'order_app/paypal_payment.html')
