from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from datetime import date, timedelta, datetime
from django.utils import timezone
from .forms import UserProfileForm, RegistrationForm
from tourism.models import ClinicBooking, HotelBooking, ConsultationBooking
from .models import UserProfile


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён успешно.')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'account/edit_profile.html', {'form': form})


@login_required
def user_profile(request):
    clinic_bookings = ClinicBooking.objects.filter(user=request.user).exclude(status='canceled').order_by('-start_date')
    hotel_bookings = HotelBooking.objects.filter(user=request.user).exclude(status='canceled').order_by('-check_in_date')
    consultation_bookings = ConsultationBooking.objects.filter(user=request.user).order_by('-date')
    today_plus_1_day = date.today() + timedelta(days=1)

    return render(request, 'account/user_profile.html', {
        'clinic_bookings': clinic_bookings,
        'hotel_bookings': hotel_bookings,
        'consultation_bookings': consultation_bookings,
        'today_plus_1_day': today_plus_1_day
    })


def cancel_booking(request, booking_type, booking_id):
    user = request.user

    if booking_type == 'clinic':
        booking = get_object_or_404(ClinicBooking, id=booking_id, user=user)
        if (booking.start_date - timezone.now().date()).days >= 5:
            booking.status = 'canceled'
            booking.save()
            messages.success(request, "Запись в клинику успешно отменена.")
        else:
            messages.error(request, "Отменить запись в клинику можно только за 5 или более дней до начала.")
            return redirect('user_profile')

    elif booking_type == 'hotel':
        booking = get_object_or_404(HotelBooking, id=booking_id, user=user)
        if (booking.check_in_date - timezone.now().date()).days >= 5:
            booking.status = 'canceled'
            booking.save()
            messages.success(request, "Бронирование отеля успешно отменено.")
        else:
            messages.error(request, "Отменить бронирование отеля можно только за 5 или более дней до заезда.")
            return redirect('user_profile')

    elif booking_type == 'consultation':
        booking = get_object_or_404(ConsultationBooking, id=booking_id, user=user)
        if hasattr(booking, 'date') and hasattr(booking, 'time'):
            booking_datetime = datetime.combine(booking.date, booking.time)
            if booking_datetime - timezone.now() >= timedelta(hours=5):
                booking.delete()
                messages.success(request, "Консультация успешно отменена.")
            else:
                messages.error(request, "Отменить консультацию можно минимум за 5 часов до начала.")
                return redirect('user_profile')

    else:
        raise Http404("Неверный тип брони")

    return redirect('user_profile')



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('user_profile')
        else:
            print("Форма невалидна:", form.errors)
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})

