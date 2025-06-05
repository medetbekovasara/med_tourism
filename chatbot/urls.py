from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_page, name='chatbot'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/symptoms/', views.symptoms_analysis, name='symptoms_analysis'),
    path('api/history/', views.chat_history, name='chat_history'),
]