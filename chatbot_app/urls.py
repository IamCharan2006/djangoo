from django.urls import path
from . import views

app_name = 'chatbot_app'  # Add this if not present

urlpatterns = [
    path('chatbot/', views.chatbot_response, name='chatbot_response'),
]