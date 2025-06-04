from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import ClinicBookingForm, HotelBookingForm, ConsultationBookingForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from datetime import date
from django.http import JsonResponse

# Главная страница
def home(request):
    clinics = Clinic.objects.all()[:3]
    return render(request, 'home.html', {'clinics': clinics})

# Список и детальная информация о клиниках
def clinic_list(request):
    clinics = Clinic.objects.all()
    return render(request, 'tourism/clinic_list.html', {'clinics': clinics})


def clinic_detail(request, clinic_id):
    clinic = get_object_or_404(Clinic, id=clinic_id)

    services = [
        "Кардиология", "Неврология", "Онкология", "Хирургия",
        "Педиатрия", "Гинекология", "Урология", "Офтальмология"
    ]

    return render(request, 'tourism/clinic_detail.html', {
        'clinic': clinic,
        'services': services
    })


# Список и детальная информация о врачах
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
            return redirect('home')
    else:
        form = HotelBookingForm()

    return render(request, 'tourism/book_hotel.html', {
        'form': form,
        'hotel': hotel,
        'today': date.today()
    })

@login_required
def book_consultation(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        # Выбран ли пользовательским действием "показать часы"
        if 'show_times' in request.POST:
            form = ConsultationBookingForm(request.POST, doctor=doctor)
        else:
            form = ConsultationBookingForm(request.POST, doctor=doctor)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.user = request.user
                booking.doctor = doctor
                booking.save()
                messages.success(request, "Вы успешно записались.")
                return redirect('user_profile')
    else:
        form = ConsultationBookingForm(doctor=doctor)

    return render(request, 'tourism/book_consultation.html', {
        'form': form,
        'doctor': doctor
    })



@login_required
def book_clinic(request, clinic_id=None):
    # Получаем клинику по ID или показываем форму выбора
    clinic = None
    if clinic_id:
        try:
            clinic = Clinic.objects.get(id=clinic_id)
        except Clinic.DoesNotExist:
            messages.error(request, "Клиника не найдена.")
            return redirect('clinic_list')

    if request.method == 'POST':
        form = ClinicBookingForm(request.POST)
        if form.is_valid():
            selected_clinic = form.cleaned_data['clinic']
            selected_doctor = form.cleaned_data['doctor']
            selected_department = form.cleaned_data['department']
            selected_start_date = form.cleaned_data['start_date']
            selected_end_date = form.cleaned_data['end_date']

            # Проверка: дата окончания не может быть раньше даты начала
            if selected_end_date < selected_start_date:
                messages.error(request, "Дата окончания не может быть раньше даты начала.")
                return redirect('clinic_booking')

            # Сохранение записи
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()

            messages.success(request, "Заявка на запись успешно отправлена!")
            return redirect('user_profile')
    else:
        # Если передан clinic_id, предзаполняем форму
        initial_data = {}
        if clinic:
            initial_data['clinic'] = clinic
        form = ClinicBookingForm(initial=initial_data, clinic_id=clinic.id if clinic else None)


    return render(request, 'tourism/book_clinic.html', {
        'form': form,
        'clinic': clinic,
    })

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


def get_doctors_by_clinic(request):
    clinic_id = request.GET.get('clinic_id')
    doctors = Doctor.objects.filter(clinic_id=clinic_id).values('id', 'name')
    return JsonResponse({'doctors': list(doctors)})


def get_doctor_specialty(request):
    doctor_id = request.GET.get('doctor_id')
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        return JsonResponse({'specialty': doctor.specialty})
    except Doctor.DoesNotExist:
        return JsonResponse({'specialty': ''})

