from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from .services import MedicalChatbotService
from .models import ChatSession, ChatMessage

def chatbot_page(request):
    """Страница чат-бота"""
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
def chat_api(request):
    """API для чата"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id')

            if not message:
                return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)

            # Получаем или создаем сессию
            chatbot_service = MedicalChatbotService()

            if session_id:
                try:
                    session = ChatSession.objects.get(session_id=session_id)
                except ChatSession.DoesNotExist:
                    session = chatbot_service.get_or_create_session(
                        user=request.user if request.user.is_authenticated else None
                    )
            else:
                session = chatbot_service.get_or_create_session(
                    user=request.user if request.user.is_authenticated else None
                )

            # Получаем ответ от ИИ
            response = chatbot_service.get_chat_response(message, session)

            return JsonResponse({
                'response': response,
                'session_id': session.session_id,
                'timestamp': timezone.now().isoformat()
            })

        except Exception as e:
            print(f"Chat API Error: {str(e)}")  # Для отладки
            return JsonResponse({'error': f'Ошибка сервера: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@csrf_exempt
def symptoms_analysis(request):
    """Специальный API для анализа симптомов"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            symptoms = data.get('symptoms', '').strip()

            if not symptoms:
                return JsonResponse({'error': 'Опишите ваши симптомы'}, status=400)

            chatbot_service = MedicalChatbotService()
            recommendations = chatbot_service.get_medical_recommendations(symptoms)

            return JsonResponse({
                'recommendations': recommendations,
                'timestamp': timezone.now().isoformat()
            })

        except Exception as e:
            print(f"Symptoms API Error: {str(e)}")  # Для отладки
            return JsonResponse({'error': f'Ошибка анализа: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def chat_history(request):
    """История чатов пользователя"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)

    try:
        sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
        history = []

        for session in sessions:
            messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
            messages_list = list(messages)  # ИСПРАВЛЕНИЕ: конвертируем в список

            last_message = messages_list[-1] if messages_list else None  # Безопасное получение последнего

            history.append({
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'messages_count': len(messages_list),
                'last_message': last_message.message if last_message else 'Новый чат'
            })

        return JsonResponse({'history': history})

    except Exception as e:
        print(f"History API Error: {str(e)}")  # Для отладки
        return JsonResponse({'error': f'Ошибка загрузки истории: {str(e)}'}, status=500)