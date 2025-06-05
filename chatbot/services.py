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

        self.system_prompt = f"""
        Ты - медицинский консультант для платформы медицинского туризма MedTour в Кыргызстане.

        ТВОЯ РОЛЬ:
        - Консультируешь по медицинским вопросам и симптомам
        - Рекомендуешь клиники и врачей из НАШЕЙ платформы
        - Помогаешь с записью на консультации
        - Рассказываешь о медицинских процедурах
        - Отвечаешь на вопросы о наших услугах
        - НЕ ставишь диагнозы, только даешь общие рекомендации

        ДОСТУПНЫЕ КЛИНИКИ НА НАШЕЙ ПЛАТФОРМЕ:
        {self.clinics_info}

        МЕДИЦИНСКИЕ ТЕМЫ, НА КОТОРЫЕ ТЫ ОТВЕЧАЕШЬ:
        - Симптомы и их анализ
        - Выбор врача и клиники
        - Медицинские процедуры и обследования
        - Запись на консультации
        - Подготовка к процедурам
        - Информация о специалистах
        - Стоимость услуг
        - Время работы клиник

        НЕ ОТВЕЧАЙ НА:
        - Политические вопросы
        - Личные вопросы не о здоровье
        - Вопросы о других сферах (спорт, погода, развлечения)
        - Просьбы написать код или решить задачи

        ПРАВИЛА:
        1. Будь дружелюбным и полезным
        2. Рекомендуй только наши клиники из списка выше
        3. Всегда подчеркивай необходимость очной консультации для диагноза
        4. Отвечай на том языка, на котором тебе пишут
        5. Если не знаешь точно - честно скажи об этом

        ЕСЛИ СПРАШИВАЮТ О ЗАПИСИ:
        "Для записи на консультацию вы можете использовать нашу платформу MedTour или связаться с клиникой напрямую."

        ЕСЛИ СПРАШИВАЮТ О ПРОЦЕДУРАХ:
        Расскажи о доступных процедурах в наших клиниках и какие специалисты их проводят.
        """

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
                🔬 Специализации: {clinic.specializations or 'Общая практика'}
                👨⚕️ Врачи: {doctors_list or 'Информация обновляется'}

                """

            return clinics_text if clinics_text else "Информация о клиниках обновляется."

        except Exception as e:
            print(f"Error getting clinics info: {e}")
            return "Информация о клиниках временно недоступна."

    def get_or_create_session(self, user=None):
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            user=user,
            session_id=session_id
        )
        return session

    def _is_medical_or_platform_question(self, message):
        """Проверяем, относится ли вопрос к медицине или нашей платформе"""

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
            'кт', 'эко', 'беременность', 'роды', 'ребенок', 'как дела', 'привет', 'педиатр'
        ]

        # Ключевые слова о платформе и услугах
        platform_keywords = [
            'medtour', 'медтур', 'платформа', 'сайт', 'услуги', 'цена', 'стоимость',
            'записаться', 'запись', 'как записаться', 'время работы', 'график',
            'контакты', 'телефон', 'адрес', 'где находится', 'как добраться',
            'какие клиники', 'какие врачи', 'какие процедуры', 'что предлагаете',
            'ваши услуги', 'медицинский туризм', 'помощь', 'поддержка'
        ]

        # Вопросительные слова + медицинский контекст
        question_patterns = [
            'какие', 'какая', 'какой', 'где', 'как', 'когда', 'сколько',
            'можно ли', 'нужно ли', 'что делать', 'помогите', 'посоветуйте'
        ]

        message_lower = message.lower()

        # Проверяем медицинские ключевые слова
        has_medical = any(keyword in message_lower for keyword in medical_keywords)

        # Проверяем ключевые слова о платформе
        has_platform = any(keyword in message_lower for keyword in platform_keywords)

        # Проверяем вопросительные паттерны
        has_question = any(pattern in message_lower for pattern in question_patterns)

        # Исключаем явно немедицинские темы
        non_medical_keywords = [
            'погода', 'спорт', 'политика', 'новости', 'музыка', 'фильм',
            'игра', 'программирование', 'код', 'python', 'javascript',
            'готовить', 'рецепт', 'путешествие', 'отдых', 'работа'
        ]

        has_non_medical = any(keyword in message_lower for keyword in non_medical_keywords)

        # Возвращаем True если есть медицинские слова ИЛИ слова о платформе ИЛИ это вопрос
        # НО НЕТ явно немедицинских тем
        return (has_medical or has_platform or has_question) and not has_non_medical

    def get_chat_response(self, message, session):
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
            self.system_prompt = f"""
            Ты - медицинский консультант для платформы медицинского туризма MedTour в Кыргызстане.

            ТВОЯ РОЛЬ:
            - Консультируешь по медицинским вопросам и симптомам
            - Рекомендуешь клиники и врачей из НАШЕЙ платформы
            - Помогаешь с записью на консультации
            - Рассказываешь о медицинских процедурах
            - Отвечаешь на вопросы о наших услугах
            - НЕ ставишь диагнозы, только даешь общие рекомендации

            ДОСТУПНЫЕ КЛИНИКИ НА НАШЕЙ ПЛАТФОРМЕ:
            {self.clinics_info}

            ПРАВИЛА:
            1. Будь дружелюбным и полезным
            2. Рекомендуй только наши клиники из списка выше
            3. Всегда подчеркивай необходимость очной консультации для диагноза
            4. Отвечай на русском языке
            5. Если не знаешь точно - честно скажи об этом

            Для записи на консультацию направляй на нашу платформу MedTour.
            """

            # Получаем историю чата для контекста
            previous_messages = ChatMessage.objects.filter(session=session).order_by('timestamp')

            # Формируем контекст
            messages = [{"role": "system", "content": self.system_prompt}]

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

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
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