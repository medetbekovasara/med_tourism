from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from .models import ChatSession, ChatMessage
from tourism.models import Clinic, Doctor
import uuid

# Инициализируем клиент OpenAI
client = None
if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
else:
    print("WARNING: OPENAI_API_KEY not found in settings!")

class MedicalChatbotService:
    def __init__(self):
        # Получаем информацию о клиниках из базы данных
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
🔬 Специализации: {getattr(clinic, 'specializations', None) or 'Общая практика'}
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

    def _is_medical_or_platform_question(self, message):
        """Проверяем, относится ли вопрос к медицине или нашей платформе"""

        # Приветствия и вежливые фразы - ВСЕГДА разрешаем
        greeting_keywords = [
            'привет', 'здравствуйте', 'добро пожаловать', 'доброе утро',
            'добрый день', 'добрый вечер', 'здравствуй', 'приветствую',
            'добро пожаловать', 'салам', 'саламалейкум', 'hello', 'hi',
            'спасибо', 'благодарю', 'пока', 'до свидания', 'хорошего дня'
        ]

        # Медицинские ключевые слова
        medical_keywords = [
            'болит', 'боль', 'симптом', 'лечение', 'врач', 'доктор', 'клиника',
            'диагноз', 'анализ', 'обследование', 'операция', 'процедура',
            'здоровье', 'болезнь', 'температура', 'кашель', 'головная боль',
            'желудок', 'сердце', 'давление', 'аллергия', 'инфекция',
            'травма', 'перелом', 'ушиб', 'рана', 'кровь', 'моча',
            'зрение', 'слух', 'зубы', 'стоматолог', 'хирург', 'терапевт',
            'кардиолог', 'невролог', 'гинеколог', 'уролог', 'дерматолог',
            'консультация', 'прием', 'запись', 'медицина', 'лекарство',
            'таблетки', 'укол', 'капельница', 'рентген', 'узи', 'мрт',
            'кт', 'эко', 'беременность', 'роды', 'ребенок', 'педиатр'
        ]

        # Ключевые слова о платформе и услугах
        platform_keywords = [
            'medtour', 'медтур', 'платформа', 'сайт', 'услуги', 'цена', 'стоимость',
            'записаться', 'запись', 'как записаться', 'время работы', 'график',
            'контакты', 'телефон', 'адрес', 'где находится', 'как добраться',
            'какие клиники', 'какие врачи', 'какие процедуры', 'что предлагаете',
            'ваши услуги', 'медицинский туризм', 'помощь', 'поддержка'
        ]

        # Вопросительные слова + общие вопросы
        question_patterns = [
            'какие', 'какая', 'какой', 'где', 'как', 'когда', 'сколько',
            'можно ли', 'нужно ли', 'что делать', 'помогите', 'посоветуйте',
            'расскажите', 'объясните', 'покажите', 'что', 'кто', 'почему'
        ]

        message_lower = message.lower().strip()

        # ВСЕГДА разрешаем приветствия
        has_greeting = any(keyword in message_lower for keyword in greeting_keywords)
        if has_greeting:
            return True

        # Проверяем медицинские ключевые слова
        has_medical = any(keyword in message_lower for keyword in medical_keywords)

        # Проверяем ключевые слова о платформе
        has_platform = any(keyword in message_lower for keyword in platform_keywords)

        # Проверяем вопросительные паттерны
        has_question = any(pattern in message_lower for pattern in question_patterns)

        # Короткие сообщения (до 3 слов) - обычно приветствия или простые вопросы
        is_short = len(message_lower.split()) <= 3

        # Исключаем явно немедицинские темы
        non_medical_keywords = [
            'погода', 'спорт', 'политика', 'новости', 'музыка', 'фильм',
            'игра', 'программирование', 'код', 'python', 'javascript',
            'готовить', 'рецепт', 'путешествие', 'отдых', 'работа', 'учеба',
            'школа', 'университет', 'экзамен', 'домашнее задание'
        ]

        has_non_medical = any(keyword in message_lower for keyword in non_medical_keywords)

        # Возвращаем True если:
        # - Есть приветствие ИЛИ
        # - Есть медицинские слова ИЛИ
        # - Есть слова о платформе ИЛИ
        # - Это вопрос ИЛИ
        # - Это короткое сообщение (вероятно, приветствие)
        # НО НЕТ явно немедицинских тем
        return (has_greeting or has_medical or has_platform or has_question or is_short) and not has_non_medical

    def get_chat_response(self, message, session):
        """Получаем ответ от чат-бота"""
        try:
            # Проверяем клиент OpenAI
            if not client:
                return "Извините, сервис временно недоступен. Проверьте настройки API."

            # Проверяем, относится ли вопрос к медицине или платформе
            if not self._is_medical_or_platform_question(message):
                return """
Извините, я специализируюсь на медицинских консультациях и помощи с нашей платформой MedTour.

Я не могу помочь с вопросами о политике, развлечениях, программировании или других немедицинских темах.

Но я буду рад помочь вам с:
🩺 Медицинскими вопросами и симптомами
🏥 Выбором клиники и врача
📋 Информацией о процедурах
📞 Записью на консультацию
💰 Стоимостью услуг

Задайте медицинский вопрос или спросите о наших услугах!
                """

            # Обновляем информацию о клиниках перед каждым запросом
            self.clinics_info = self._get_clinics_info()

            # Формируем системный промпт
            system_prompt = f"""
Ты - дружелюбный медицинский консультант для платформы медицинского туризма MedTour в Кыргызстане.

ТВОЯ РОЛЬ:
- Дружелюбно приветствуешь пользователей
- Консультируешь по медицинским вопросам и симптомам
- Рекомендуешь клиники и врачей из НАШЕЙ платформы
- Помогаешь с записью на консультации
- Рассказываешь о медицинских процедурах
- Отвечаешь на вопросы о наших услугах
- НЕ ставишь диагнозы, только даешь общие рекомендации

ДОСТУПНЫЕ КЛИНИКИ НА НАШЕЙ ПЛАТФОРМЕ:
{self.clinics_info}

КАК ОТВЕЧАТЬ НА ПРИВЕТСТВИЯ:
- "Привет!" → "Здравствуйте! Я медицинский консультант MedTour. Чем могу помочь?"
- "Добрый день" → "Добрый день! Расскажите о ваших медицинских вопросах."
- "Спасибо" → "Пожалуйста! Обращайтесь, если будут еще вопросы."

ПРАВИЛА:
1. Будь дружелюбным и вежливым
2. На приветствия отвечай приветствием + предложением помощи
3. Рекомендуй только наши клиники из списка выше
4. Всегда подчеркивай необходимость очной консультации для диагноза
5. Отвечай на русском языке
6. Если не знаешь точно - честно скажи об этом

Для записи на консультацию направляй на нашу платформу MedTour.
            """

            # Получаем историю чата для контекста
            previous_messages = ChatMessage.objects.filter(session=session).order_by('timestamp')

            # Формируем контекст
            messages = [{"role": "system", "content": system_prompt}]

            # Добавляем предыдущие сообщения (последние 3 для контекста)
            prev_messages_list = list(previous_messages)
            if len(prev_messages_list) > 3:
                recent_messages = prev_messages_list[-3:]
            else:
                recent_messages = prev_messages_list

            for prev_msg in recent_messages:
                messages.append({"role": "user", "content": prev_msg.message})
                messages.append({"role": "assistant", "content": prev_msg.response})

            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": message})

            # Запрос к OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=600,
                temperature=0.7,
            )

            ai_response = response.choices[0].message.content.strip()

            # Сохраняем в базу
            chat_message = ChatMessage.objects.create(
                session=session,
                message=message,
                response=ai_response,
                timestamp=timezone.now()
            )

            return ai_response

        except Exception as e:
            error_message = str(e).lower()

            if "authentication" in error_message or "api key" in error_message:
                return "Ошибка аутентификации API. Проверьте API ключ OpenAI."
            elif "rate limit" in error_message or "quota" in error_message:
                return "Превышен лимит запросов или закончилась квота. Попробуйте позже."
            elif "insufficient_quota" in error_message:
                return "Недостаточно средств на счету OpenAI. Пополните баланс."
            else:
                print(f"Chat service error: {str(e)}")
                return f"Извините, произошла ошибка: {str(e)}"

    def get_medical_recommendations(self, symptoms):
        """Специальный метод для рекомендаций по симптомам с учетом наших клиник"""

        # Обновляем информацию о клиниках
        self.clinics_info = self._get_clinics_info()

        prompt = f"""
Пациент описывает следующие симптомы: {symptoms}

На основе наших доступных клиник:
{self.clinics_info}

Пожалуйста, предоставь:
1. К какому врачу-специалисту лучше обратиться
2. Какую из НАШИХ клиник рекомендуешь и почему
3. Какие обследования могут потребоваться
4. Общие рекомендации (без постановки диагноза)
5. Срочность обращения (плановое/срочное/экстренное)

ВАЖНО: Рекомендуй только клиники из нашего списка!
Обязательно подчеркни, что это предварительные рекомендации.
        """

        try:
            if not client:
                return "Извините, сервис анализа симптомов временно недоступен."

            system_prompt = f"""
Ты - медицинский консультант для платформы MedTour в Кыргызстане.

ДОСТУПНЫЕ КЛИНИКИ:
{self.clinics_info}

Анализируй симптомы и рекомендуй ТОЛЬКО наши клиники из списка выше.
НЕ ставь диагнозы, только общие рекомендации.
Всегда подчеркивай необходимость очной консультации.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700,
                temperature=0.6,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            error_message = str(e).lower()

            if "authentication" in error_message or "api key" in error_message:
                return "Ошибка аутентификации API. Проверьте API ключ OpenAI."
            elif "rate limit" in error_message or "quota" in error_message:
                return "Превышен лимит запросов. Попробуйте позже."
            elif "insufficient_quota" in error_message:
                return "Недостаточно средств на счету OpenAI. Пополните баланс."
            else:
                print(f"Symptoms analysis error: {str(e)}")
                return f"Ошибка при анализе симптомов: {str(e)}"

        def get_clinic_recommendations(self, specialty=None, location=None):
            try:
                clinics = Clinic.objects.all()

                if specialty:
                    # Фильтруем по специализации (если есть поле specializations)
                    if hasattr(Clinic, 'specializations'):
                        clinics = clinics.filter(specializations__icontains=specialty)

                if location:
                    # Фильтруем по адресу
                    clinics = clinics.filter(address__icontains=location)

                if not clinics.exists():
                    return "К сожалению, клиники по вашим критериям не найдены. Рекомендую обратиться к нашим партнерским клиникам."

                recommendations = "🏥 Рекомендуемые клиники:\n\n"

                for clinic in clinics:
                    doctors = Doctor.objects.filter(clinic=clinic)
                    doctors_list = ", ".join(
                        [f"{doc.name} ({doc.specialty})" for doc in doctors[:3]])  # Показываем первых 3 врачей

                    recommendations += f"""
                📍 **{clinic.name}**
                🏠 Адрес: {clinic.address}
                📋 Описание: {clinic.description[:100]}{'...' if len(clinic.description) > 100 else ''}
                👨⚕️ Врачи: {doctors_list or 'Информация обновляется'}

                """

                recommendations += "\n💡 Для записи на консультацию используйте нашу платформу MedTour или свяжитесь с клиникой напрямую."

                return recommendations

            except Exception as e:
                print(f"Error getting clinic recommendations: {str(e)}")
                return "Извините, произошла ошибка при получении рекомендаций клиник."

        def get_doctor_info(self, doctor_name=None, specialty=None):
            """Получаем информацию о врачах"""
            try:
                doctors = Doctor.objects.all()

                if doctor_name:
                    doctors = doctors.filter(name__icontains=doctor_name)

                if specialty:
                    doctors = doctors.filter(specialty__icontains=specialty)

                if not doctors.exists():
                    return "Врачи по вашим критериям не найдены. Попробуйте изменить параметры поиска."

                doctor_info = "👨⚕️ Информация о врачах:\n\n"

                for doctor in doctors:
                    doctor_info += f"""
                🩺 **{doctor.name}**
                🏥 Клиника: {doctor.clinic.name if doctor.clinic else 'Не указана'}
                📋 Специализация: {doctor.specialty}
                ⭐ Опыт: {getattr(doctor, 'experience', 'Не указан')}
                📍 Адрес: {doctor.clinic.address if doctor.clinic else 'Не указан'}

                """

                doctor_info += "\n📞 Для записи на консультацию обращайтесь через нашу платформу MedTour."

                return doctor_info

            except Exception as e:
                print(f"Error getting doctor info: {str(e)}")
                return "Извините, произошла ошибка при получении информации о врачах."

        def clear_chat_history(self, session):
            """Очищаем историю чата для сессии"""
            try:
                ChatMessage.objects.filter(session=session).delete()
                return True
            except Exception as e:
                print(f"Error clearing chat history: {str(e)}")
                return False

        def get_chat_history(self, session, limit=10):
            """Получаем историю чата для сессии"""
            try:
                messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:limit]
                return list(reversed(messages))
            except Exception as e:
                print(f"Error getting chat history: {str(e)}")
                return []

        def get_session_stats(self, session):
            """Получаем статистику сессии"""
            try:
                message_count = ChatMessage.objects.filter(session=session).count()
                first_message = ChatMessage.objects.filter(session=session).order_by('timestamp').first()
                last_message = ChatMessage.objects.filter(session=session).order_by('-timestamp').first()

                return {
                    'message_count': message_count,
                    'session_start': first_message.timestamp if first_message else None,
                    'last_activity': last_message.timestamp if last_message else None,
                    'session_duration': (last_message.timestamp - first_message.timestamp) if (
                                first_message and last_message) else None
                }
            except Exception as e:
                print(f"Error getting session stats: {str(e)}")
                return {}
