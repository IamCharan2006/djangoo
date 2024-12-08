from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, RestaurantProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['password1'].validators = []
        self.fields['password2'].validators = []
        self._password_validators = []

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password1(self):
        return self.cleaned_data.get('password1')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

class RestaurantRegistrationForm(forms.ModelForm):
    CITY_CHOICES = [
        ('', 'Select City'),
        ('mumbai', 'Mumbai'),
        ('delhi', 'Delhi'),
        ('bangalore', 'Bangalore'),
        ('hyderabad', 'Hyderabad'),
        ('chennai', 'Chennai'),
        ('kolkata', 'Kolkata'),
        ('pune', 'Pune'),
        ('ahmedabad', 'Ahmedabad'),
        ('guntur', 'Guntur'),
        ('vijayawada', 'Vijayawada'),
    ]

    CUISINE_CHOICES = [
        ('', 'Select Cuisine Type'),
        ('indian', 'Indian'),
        ('chinese', 'Chinese'),
        ('italian', 'Italian'),
        ('mexican', 'Mexican'),
        ('thai', 'Thai'),
        ('japanese', 'Japanese'),
        ('continental', 'Continental'),
        ('fast_food', 'Fast Food'),
    ]

    name = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea)
    city = forms.ChoiceField(choices=CITY_CHOICES)
    phone = forms.CharField(max_length=15)
    email = forms.EmailField()
    cuisine_type = forms.ChoiceField(choices=CUISINE_CHOICES, help_text="These will be shown as your restaurant's specialties")
    description = forms.CharField(widget=forms.Textarea, required=False)
    business_license = forms.FileField(required=False)
    food_license = forms.FileField(required=False)
    owner_id_proof = forms.FileField(required=False)
    gstin_number = forms.CharField(max_length=15, required=False)
    opening_time = forms.TimeField(required=False)
    closing_time = forms.TimeField(required=False)
    delivery_radius = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    restaurant_image = forms.ImageField(
        help_text="Upload your restaurant's logo or main image",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    restaurant_banner = forms.ImageField(
        help_text="Upload a banner image for your restaurant",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )

    class Meta:
        model = RestaurantProfile
        fields = ['name', 'address', 'city', 'phone', 'email', 
                 'cuisine_type', 'description', 'business_license', 
                 'food_license', 'owner_id_proof', 'gstin_number',
                 'opening_time', 'closing_time', 'delivery_radius',
                 'restaurant_image', 'restaurant_banner']

    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', None)
        super().__init__(*args, **kwargs)
        
        if self.step == 1:
            required_fields = ['name', 'address', 'city', 'phone', 'email', 'cuisine_type']
            for field in required_fields:
                self.fields[field].required = True
        elif self.step == 2:
            pass
        elif self.step == 3:
            required_fields = ['opening_time', 'closing_time', 'delivery_radius']
            for field in required_fields:
                self.fields[field].required = True

        # Make file fields optional
        self.fields['restaurant_image'].required = False
        self.fields['restaurant_banner'].required = False

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'profile_picture'] 