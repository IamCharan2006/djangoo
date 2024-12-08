from django import forms
from .models import Restaurant, MenuCategory, MenuItem

class RestaurantRegistrationForm(forms.ModelForm):
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

    specialties = forms.MultipleChoiceField(
        choices=CUISINE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select all cuisines that apply"
    )

    class Meta:
        model = Restaurant
        exclude = ['rating', 'total_ratings', 'created_at', 'updated_at', 'is_verified']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        exclude = ['restaurant', 'order']

class MenuItemForm(forms.ModelForm):
    MAIN_CATEGORIES = [
        ('', 'Select Main Category'),
        ('starters', 'Starters'),
        ('appetizers', 'Appetizers'),
        ('main_course', 'Main Course'),
        ('desserts', 'Desserts'),
        ('beverages', 'Beverages'),
        ('sides', 'Sides'),
        ('specials', 'Specials')
    ]

    main_category = forms.ChoiceField(
        choices=MAIN_CATEGORIES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    sub_category = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter sub-category (e.g., Vegetarian, Spicy, etc.)'
        })
    )

    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        } 