from django import forms
from .models import OrderRating

class OrderRatingForm(forms.ModelForm):
    class Meta:
        model = OrderRating
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'feedback': forms.Textarea(attrs={
                'placeholder': 'Tell us about your experience...',
                'rows': 4
            })
        } 