from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    clinic_list, clinic_detail, doctor_list, doctor_detail,
    book_clinic, book_hotel, book_consultation, hotel_list
)
from . import views
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from django.urls import path, include

urlpatterns = [
    path('clinics/', clinic_list, name='clinic_list'),
    path('clinics/', clinic_list, name='clinic_list'),
    path('clinics/<int:clinic_id>/', clinic_detail, name='clinic_detail'),
    path('doctors/', doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/', doctor_detail, name='doctor_detail'),
    path('booking/clinic/', book_clinic, name='clinic_booking'),
    path('booking/hotel/', book_hotel, name='hotel_booking'),
    path('booking/consultation/', book_consultation, name='consultation_booking'),
    path('search/', views.search_results, name='search_results'),
    path('hotels/', hotel_list, name='hotel_list'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('hotels/<int:hotel_id>/book/', book_hotel, name='book_hotel'),
    path('booking/hotel/<int:hotel_id>/', views.book_hotel, name='hotel_booking'),
    path('booking/hotel/', views.book_hotel, name='hotel_booking'),
    path('about/', views.about_view, name='about'),



]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
