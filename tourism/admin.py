from django.contrib import admin
from .models import Clinic, Doctor, ClinicBooking, HotelBooking, ConsultationBooking, Hotel


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'specializations')  # Поля, которые отображаются в списке
    search_fields = ('name', 'address', 'specializations')  # Поиск по этим полям

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'experience', 'clinic')
    search_fields = ('name', 'specialty', 'clinic__name')
    list_filter = ('specialty', 'clinic')  # Фильтр по специальности и клинике


@admin.register(ClinicBooking)
class ClinicBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'clinic', 'start_date', 'end_date', 'status')  # 🔴 Исправляем 'date' -> 'start_date'
    list_filter = ('clinic', 'start_date', 'end_date', 'status')  # 🔴 Исправляем 'date' -> 'start_date'
    search_fields = ('user__username', 'clinic__name')

@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel', 'check_in_date', 'check_out_date', 'status']
    list_filter = ('check_in_date', 'check_out_date')
    search_fields = ('user__username', 'hotel_name')

@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'doctor', 'date', 'time', 'reason')
    list_filter = ('date', 'doctor')
    search_fields = ('user__username', 'doctor__name')

admin.site.register(Hotel)