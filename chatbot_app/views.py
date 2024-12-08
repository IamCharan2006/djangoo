from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import re
import google.generativeai as genai
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

# Configure the Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)

# Define the context for the chatbot
CHATBOT_CONTEXT = """You are a helpful assistant for a food delivery app. Your name is FoodBot.
You can help with:
1. Restaurant recommendations
2. Menu items and dietary information
3. Order tracking and delivery times
4. Payment and refund queries
5. Special offers and promotions

Please provide concise, friendly responses focused on food delivery. 
If asked about topics unrelated to food delivery, politely redirect the conversation to food-related topics.

User message: """


def clean_response(text):
    """Cleans the response to remove markdown and format it for HTML."""
    # Remove asterisks while preserving the text
    cleaned = re.sub(r'\*+', '', text)
    # Convert newlines to HTML breaks
    cleaned = cleaned.replace('\n', '<br>')
    return cleaned


@csrf_exempt
def chatbot_response(request):
    """Handles chatbot queries."""
    if request.method == 'POST':
        user_message = request.POST.get('message')
        logger.info(f"Received message: {user_message}")

        try:
            # Add context to the user's message
            full_message = CHATBOT_CONTEXT + user_message

            # Generate response from Gemini
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(full_message)

            # Clean the response
            bot_response = clean_response(response.text)
            logger.info(f"Generated response: {bot_response}")
        except Exception as e:
            bot_response = "Sorry, I'm having trouble understanding that right now."
            logger.error(f"Error generating response: {str(e)}")

        return JsonResponse({'response': bot_response})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)