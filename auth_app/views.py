from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from restaurant_app.models import Restaurant, MenuCategory
from .models import UserProfile, RestaurantProfile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, RestaurantRegistrationForm


#HomePage
# HomePage View
def HomePage(request):
    return render(request, 'ProjectHomePage.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role='customer')
            messages.success(request, f'Account created! You can now login.')
            return redirect('auth:login')
    else:
        form = UserRegisterForm()
    return render(request, 'auth_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Always redirect to dashboard for regular users
            if hasattr(user, 'restaurantprofile'):
                return redirect('restaurant:dashboard')
            else:
                return redirect('user:dashboard')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'auth_app/login.html')


#Logout

def logout_view(request):
    logout(request)
    return redirect('HomePage')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('auth:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'auth_app/profile.html', context)

def register_restaurant(request):
    current_step = request.session.get('restaurant_registration_step', 0)
    
    # Initialize form based on current step
    if current_step == 0:
        form = UserRegisterForm()
    elif current_step == 1:
        form = RestaurantRegistrationForm()
    elif current_step == 2:
        form = RestaurantRegistrationForm()
    else:
        form = RestaurantRegistrationForm()
    
    if request.method == 'POST':
        if current_step == 0:
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                request.session['restaurant_registration_step'] = 1
                # Log the user in after registration
                login(request, user)
                messages.success(request, f'Account created! Please complete your restaurant profile.')
                return redirect('auth:register_restaurant')
                
        elif current_step == 1:
            form = RestaurantRegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                restaurant_data = {
                    'name': form.cleaned_data['name'],
                    'address': form.cleaned_data['address'],
                    'city': form.cleaned_data['city'],
                    'phone': form.cleaned_data['phone'],
                    'email': form.cleaned_data['email'],
                    'cuisine_type': form.cleaned_data['cuisine_type'],
                    'description': form.cleaned_data['description'],
                    'restaurant_image': form.cleaned_data.get('restaurant_image'),
                    'restaurant_banner': form.cleaned_data.get('restaurant_banner'),
                }
                request.session['restaurant_data'] = restaurant_data
                request.session['restaurant_registration_step'] = 2
                messages.success(request, 'Basic information saved. Now upload your documents.')
                return redirect('auth:register_restaurant')
            else:
                messages.error(request, 'Please fill in all required fields.')
                
        elif current_step == 2:
            # Check if user wants to skip document upload
            if request.POST.get('skip_documents') == 'true':
                request.session['restaurant_data'].update({
                    'business_license': '',
                    'food_license': '',
                    'owner_id_proof': '',
                    'gstin_number': 'PENDING'
                })
                request.session['restaurant_registration_step'] = 3
                messages.info(request, 'Document upload skipped. You can update these later.')
                return redirect('auth:register_restaurant')
                
            # Normal document upload handling
            form = RestaurantRegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                request.session['restaurant_data'].update({
                    'business_license': form.cleaned_data.get('business_license', ''),
                    'food_license': form.cleaned_data.get('food_license', ''),
                    'owner_id_proof': form.cleaned_data.get('owner_id_proof', ''),
                    'gstin_number': form.cleaned_data.get('gstin_number', 'PENDING'),
                })
                request.session['restaurant_registration_step'] = 3
                messages.success(request, 'Documents uploaded successfully. Final step: Operating hours.')
                return redirect('auth:register_restaurant')
                
        elif current_step == 3:
            opening_time = request.POST.get('opening_time')
            closing_time = request.POST.get('closing_time')
            delivery_radius = request.POST.get('delivery_radius')
            
            if opening_time and closing_time and delivery_radius:
                try:
                    restaurant_data = request.session.get('restaurant_data', {})
                    
                    # Create Restaurant instance with default image
                    restaurant = Restaurant.objects.create(
                        name=restaurant_data['name'],
                        address=restaurant_data['address'],
                        phone=restaurant_data['phone'],
                        email=restaurant_data['email'],
                        specialties=restaurant_data['cuisine_type'],
                        description=restaurant_data.get('description', ''),
                        opening_time=opening_time,
                        closing_time=closing_time,
                        delivery_radius=float(delivery_radius),
                        image='default_restaurant.jpg',  # Set default image
                        minimum_order=0.00,
                        delivery_fee=0.00,
                        preparation_time=30,
                        tax_rate=0.00
                    )

                    # Create RestaurantProfile
                    restaurant_profile = RestaurantProfile.objects.create(
                        user=request.user,
                        restaurant=restaurant,
                        role='restaurant'
                    )

                    # Handle image uploads if they exist in the session
                    if restaurant_data.get('restaurant_image'):
                        restaurant.image = restaurant_data['restaurant_image']
                        restaurant.save()
                    
                    if restaurant_data.get('restaurant_banner'):
                        restaurant_profile.restaurant_banner = restaurant_data['restaurant_banner']
                        restaurant_profile.save()

                    # Create default menu categories
                    default_categories = ['Starters', 'Main Course', 'Desserts', 'Beverages']
                    for category_name in default_categories:
                        MenuCategory.objects.create(
                            restaurant=restaurant,
                            name=category_name
                        )
                    
                    # Clean up session
                    del request.session['restaurant_data']
                    del request.session['restaurant_registration_step']
                    
                    messages.success(request, 'Restaurant registration complete! Please wait for verification.')
                    return redirect('restaurant:dashboard')
                except Exception as e:
                    messages.error(request, f'Error creating restaurant: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'auth_app/register_restaurant.html', {
        'form': form,
        'current_step': current_step,
        'total_steps': 4
    })