from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('clinics/', views.clinic_list, name='clinic_list'),
    path('clinics/<int:clinic_id>/', views.clinic_detail, name='clinic_detail'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('book-clinic/', views.book_clinic, name='clinic_booking'),
    path('book-clinic/<int:clinic_id>/', views.book_clinic, name='book_clinic'),
    path('ajax/get-doctors/', views.get_doctors_by_clinic, name='get_doctors_by_clinic'),
    path('ajax/get-doctor-specialty/', views.get_doctor_specialty, name='get_doctor_specialty'),
    path('hotels/book/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('book-consultation/<int:doctor_id>/', views.book_consultation, name='book_consultation'),
    path('search/', views.search_results, name='search_results'),
    path('about/', views.about_view, name='about'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
