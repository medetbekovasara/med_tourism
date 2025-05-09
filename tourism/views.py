from datetime import time, timedelta, datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Clinic, Doctor, ConsultationBooking, Hotel
from .forms import ClinicBookingForm, HotelBookingForm, ConsultationBookingForm
from django.contrib import messages
from django.db.models import Q, CharField
from django.db.models.functions import Lower, Cast

# Главная страница
def home(request):
    clinics = Clinic.objects.all()[:3]  # Показываем только 3 популярных
    return render(request, 'home.html', {'clinics': clinics})

# 📍 Список и детальная информация о клиниках
def clinic_list(request):
    clinics = Clinic.objects.all()
    return render(request, 'tourism/clinic_list.html', {'clinics': clinics})

def clinic_detail(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)
    return render(request, 'tourism/clinic_detail.html', {'clinic': clinic})

# 📍 Список и детальная информация о врачах
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'tourism/doctor_list.html', {'doctors': doctors})

def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, 'tourism/doctor_detail.html', {'doctor': doctor})

def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'tourism/hotel_list.html', {'hotels': hotels})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    return render(request, 'tourism/hotel_detail.html', {'hotel': hotel})

# 📅 Бронирование клиники
@login_required
def book_clinic(request):
    if request.method == 'POST':
        form = ClinicBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return redirect('user_profile')  # После бронирования отправляем в профиль
    else:
        form = ClinicBookingForm()
    return render(request, 'tourism/book_clinic.html', {'form': form})

@login_required
def book_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        form = HotelBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel
            booking.save()
            return redirect('home')  # или куда ты хочешь
    else:
        form = HotelBookingForm()

    return render(request, 'tourism/hotel_booking.html', {'form': form, 'hotel': hotel})

@login_required
def book_consultation(request):
    if request.method == 'POST':
        form = ConsultationBookingForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['date']
            selected_time = form.cleaned_data['time']
            doctor = form.cleaned_data['doctor']

            # 🔴 Блокируем выходные (суббота и воскресенье)
            if selected_date.weekday() in [5, 6]:
                messages.error(request, "В выходные дни консультации невозможны.")
                return redirect('consultation_booking')

            # 🔴 Ограничиваем бронирование с 10:00 до 20:00
            if not (time(10, 0) <= selected_time <= time(20, 0)):
                messages.error(request, "Можно записаться только с 10:00 до 20:00.")
                return redirect('consultation_booking')

            # 🔴 Проверяем, есть ли запись в течение 1 часа
            one_hour_before = (datetime.combine(selected_date, selected_time) - timedelta(hours=1)).time()
            one_hour_after = (datetime.combine(selected_date, selected_time) + timedelta(hours=1)).time()

            if ConsultationBooking.objects.filter(
                doctor=doctor, date=selected_date,
                time__gte=one_hour_before, time__lt=one_hour_after
            ).exists():
                messages.error(request, "Этот временной интервал уже занят. Выберите другой.")
                return redirect('consultation_booking')

            # ✅ Если всё хорошо, сохраняем запись
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, "Вы успешно записались на консультацию!")
            return redirect('user_profile')

    else:
        form = ConsultationBookingForm()

    return render(request, 'tourism/book_consultation.html', {'form': form})


@login_required
def book_clinic(request):
    if request.method == 'POST':
        form = ClinicBookingForm(request.POST)
        if form.is_valid():
            selected_clinic = form.cleaned_data['clinic']
            selected_doctor = form.cleaned_data['doctor']
            selected_department = form.cleaned_data['department']
            selected_start_date = form.cleaned_data['start_date']  # ✅ Заменили `date` на `start_date`
            selected_end_date = form.cleaned_data['end_date']  # ✅ Добавили `end_date`

            # 🔴 Проверяем, что дата окончания не раньше даты начала
            if selected_end_date < selected_start_date:
                messages.error(request, "Дата окончания не может быть раньше даты начала.")
                return redirect('clinic_booking')

            # ✅ Если всё в порядке, сохраняем бронь
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, "Клиника успешно забронирована!")
            return redirect('user_profile')

    else:
        form = ClinicBookingForm()

    return render(request, 'tourism/book_clinic.html', {'form': form})


from django.db.models import Q
from .models import Doctor, Clinic

def search_results(request):
    query = request.GET.get('q', '').strip()

    doctors = Doctor.objects.filter(
        Q(name__icontains=query) | Q(specialty__icontains=query)
    )
    clinics = Clinic.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )

    return render(request, 'tourism/search_results.html', {
        'query': query,
        'doctors': doctors,
        'clinics': clinics,
    })

def about_view(request):
    return render(request, 'tourism/about.html')






