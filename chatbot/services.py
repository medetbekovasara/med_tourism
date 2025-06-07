from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from .models import ChatSession, ChatMessage
from tourism.models import Clinic, Doctor
import uuid
import os
import re

# Инициализируем клиент OpenAI
def get_openai_client():
    """Получаем клиент OpenAI с проверкой ключа"""
    api_key = None

    if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
        api_key = settings.OPENAI_API_KEY
    elif os.getenv('OPENAI_API_KEY'):
        api_key = os.getenv('OPENAI_API_KEY')

    if not api_key or api_key == 'your-actual-api-key-here':
        print("❌ OPENAI_API_KEY не найден!")
        return None

    if not api_key.startswith('sk-'):
        print(f"❌ Неверный формат API ключа: {api_key[:10]}...")
        return None

    try:
        client = OpenAI(api_key=api_key)
        print(f"✅ OpenAI клиент инициализирован! Ключ: {api_key[:15]}...")
        return client
    except Exception as e:
        print(f"❌ Ошибка инициализации OpenAI: {e}")
        return None

client = get_openai_client()

class MedicalChatbotService:
    def __init__(self):
        """Инициализация сервиса медицинского чат-бота"""
        self.clinics_info = self._get_clinics_info()

    def _get_clinics_info(self):
        """Получаем информацию о клиниках из базы данных"""
        try:
            clinics = Clinic.objects.all()
            clinics_text = ""

            for clinic in clinics:
                doctors = Doctor.objects.filter(clinic=clinic)
                doctors_list = ", ".join([f"{doc.name} ({doc.specialty})" for doc in doctors])

                clinics_text += f"""
🏥 {clinic.name}
📍 Адрес: {clinic.address}
📝 Описание: {clinic.description}
👨⚕️ Врачи: {doctors_list or 'Информация обновляется'}

"""

            return clinics_text if clinics_text else "Информация о клиниках обновляется."

        except Exception as e:
            print(f"Error getting clinics info: {e}")
            return "Информация о клиниках временно недоступна."

    def get_or_create_session(self, user=None):
        """Создаем новую сессию чата"""
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            user=user,
            session_id=session_id
        )
        return session

    def _is_relevant_question(self, message):
        """
        УПРОЩЕННАЯ логика определения релевантности вопроса
        Теперь ИИ сам будет решать, отвечать или нет
        """
        message_lower = message.lower().strip()

        # ЯВНО ЗАПРЕЩЕННЫЕ темы (только самые очевидные)
        forbidden_topics = [
            # Программирование
            'python', 'javascript', 'код', 'программирование', 'html', 'css',
            'django', 'react', 'vue', 'angular', 'php', 'java', 'c++',

            # Развлечения
            'фильм', 'сериал', 'игра', 'игры', 'музыка', 'песня',
            'концерт', 'театр', 'кино',

            # Политика
            'президент', 'выборы', 'политика', 'правительство', 'партия',

            # Спорт (кроме спортивной медицины)
            'футбол', 'баскетбол', 'хоккей', 'теннис', 'бокс',

            # Образование (кроме медицинского)
            'домашнее задание', 'экзамен', 'школа', 'университет', 'диплом',

            # Технологии
            'компьютер', 'телефон', 'интернет', 'wifi', 'windows', 'android',

            # Кулинария
            'рецепт', 'готовить', 'еда', 'блюдо', 'ресторан'
        ]

        # Проверяем на явно запрещенные темы
        has_forbidden = any(topic in message_lower for topic in forbidden_topics)

        if has_forbidden:
            return False

        # Если нет явно запрещенных тем - разрешаем
        # ИИ сам решит, как отвечать
        return True

    def get_chat_response(self, message, session):
        """Получаем ответ от чат-бота с улучшенной логикой"""
        try:
            # Проверяем клиент OpenAI
            if not client:
                return """
❌ Сервис ИИ временно недоступен.
Обратитесь к администратору сайта.
                """

            # Простая проверка на явно нерелевантные темы
            if not self._is_relevant_question(message):
                return """
Извините, я специализируюсь на медицинских консультациях и помощи с платформой MedTour.

Я не могу помочь с программированием, развлечениями, политикой или другими немедицинскими темами.

Я буду рад помочь вам с:
🩺 Медицинскими вопросами и симптомами
🏥 Выбором клиники и врача
📋 Информацией о процедурах
📞 Записью на консультацию

Задайте медицинский вопрос!
                """

            # Обновляем информацию о клиниках
            self.clinics_info = self._get_clinics_info()

            # УЛУЧШЕННЫЙ системный промпт с четкими инструкциями
            system_prompt = f"""
Ты - медицинский консультант-ассистент для платформы MedTour в Кыргызстане.

ТВОЯ ГЛАВНАЯ ЗАДАЧА:
Помогать пользователям с медицинскими вопросами и услугами нашей платформы.

ДОСТУПНЫЕ КЛИНИКИ:
{self.clinics_info}

КАК ОПРЕДЕЛИТЬ, ОТВЕЧАТЬ ЛИ НА ВОПРОС:

✅ ОТВЕЧАЙ НА:
- Приветствия (привет, здравствуйте, добрый день)
- Медицинские вопросы (симптомы, болезни, лечение)
- Вопросы о врачах и специалистах
- Вопросы о клиниках и процедурах
- Вопросы о записи на прием
- Вопросы о здоровье и самочувствии
- Общие вопросы о медицине
- Вопросы о нашей платформе MedTour
- Благодарности и вежливые фразы

❌ НЕ ОТВЕЧАЙ НА:
- Программирование и IT
- Политику и новости
- Развлечения (фильмы, игры, музыка)
- Кулинарию и рецепты
- Спорт (кроме спортивной медицины)
- Образование (кроме медицинского)
- Технологии и гаджеты

ЕСЛИ ВОПРОС НЕ МЕДИЦИНСКИЙ:
Вежливо объясни, что ты специализируешься только на медицинских консультациях и предложи задать медицинский вопрос.

ПРАВИЛА ОТВЕТОВ:
1. Будь дружелюбным и профессиональным
2. Рекомендуй только наши клиники из списка
3. НЕ ставь диагнозы - только общие рекомендации
4. Всегда подчеркивай необходимость очной консультации
5. Отвечай на русском языке
6. Если не уверен в медицинской информации - честно скажи об этом

ПРИМЕРЫ ХОРОШИХ ОТВЕТОВ:

На "Привет":
"Здравствуйте! Я медицинский консультант MedTour. Расскажите о ваших медицинских вопросах или симптомах."

На "Болит голова":
"При головной боли рекомендую обратиться к неврологу или терапевту. В наших клиниках работают опытные специалисты: [список врачей]. Для точного диагноза необходима очная консультация."

На "Какие у вас клиники":
"У нас есть несколько партнерских клиник: [список с адресами и специализациями]"
            """

            # Получаем историю чата для контекста
            previous_messages = ChatMessage.objects.filter(session=session).order_by('timestamp')

            # Формируем контекст для API
            messages = [{"role": "system", "content": system_prompt}]

            # Добавляем последние 2 сообщения для контекста
            recent_messages = list(previous_messages)[-2:]
            for prev_msg in recent_messages:
                messages.append({"role": "user", "content": prev_msg.message})
                messages.append({"role": "assistant", "content": prev_msg.response})

            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": message})

            print(f"🔄 Отправляем запрос в OpenAI...")
            print(f"📝 Сообщение: {message}")

            # Запрос к OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )

            ai_response = response.choices[0].message.content.strip()
            print(f"✅ Получен ответ от OpenAI: {ai_response[:50]}...")

            # Сохраняем в базу данных
            ChatMessage.objects.create(
                session=session,
                message=message,
                response=ai_response,
                timestamp=timezone.now()
            )

            return ai_response

        except Exception as e:
            error_message = str(e).lower()
            print(f"❌ Ошибка в get_chat_response: {str(e)}")

            if "authentication" in error_message or "api key" in error_message:
                return "❌ Ошибка аутентификации OpenAI API. Обратитесь к администратору."
            elif "rate limit" in error_message or "quota" in error_message:
                return "⏳ Превышен лимит запросов. Попробуйте через несколько минут."
            elif "insufficient_quota" in error_message:
                return "💳 Недостаточно средств на счету OpenAI."
            else:
                return f"❌ Произошла ошибка: {str(e)}"

    # Остальные методы остаются без изменений
    def get_medical_recommendations(self, symptoms):
        """Рекомендации по симптомам"""
        self.clinics_info = self._get_clinics_info()

        prompt = f"""
Пациент описывает симптомы: {symptoms}

На основе наших клиник:
{self.clinics_info}

Предоставь:
1. К какому специалисту обратиться
2. Какую клиники рекомендуешь
3. Общие рекомендации (БЕЗ диагноза)
4. Срочность обращения

ВАЖНО: Рекомендуй только наши клиники!
        """

        try:
            if not client:
                return "Сервис анализа симптомов временно недоступен."

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Ты медицинский консультант MedTour. Клиники: {self.clinics_info}"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.6,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Ошибка при анализе симптомов: {str(e)}"

    def clear_chat_history(self, session):
        """Очищаем историю чата"""
        try:
            ChatMessage.objects.filter(session=session).delete()
            return True
        except Exception as e:
            print(f"Error clearing chat history: {str(e)}")
            return False

    def get_chat_history(self, session, limit=10):
        """Получаем историю чата"""
        try:
            messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:limit]
            return list(reversed(messages))
        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            return []