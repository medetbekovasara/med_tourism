from django.contrib.auth import login
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from tourism.models import ClinicBooking, HotelBooking, ConsultationBooking

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile')  # Перенаправление обратно в профиль
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'account/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def user_profile(request):
    clinic_bookings = ClinicBooking.objects.filter(user=request.user)
    hotel_bookings = HotelBooking.objects.filter(user=request.user)
    consultation_bookings = ConsultationBooking.objects.filter(user=request.user)

    return render(request, 'account/user_profile.html', {
        'clinic_bookings': clinic_bookings,
        'hotel_bookings': hotel_bookings,
        'consultation_bookings': consultation_bookings
    })

@login_required
def cancel_booking(request, booking_type, booking_id):
    if booking_type == "clinic":
        booking = get_object_or_404(ClinicBooking, id=booking_id, user=request.user)
    elif booking_type == "hotel":
        booking = get_object_or_404(HotelBooking, id=booking_id, user=request.user)
    elif booking_type == "consultation":
        booking = get_object_or_404(ConsultationBooking, id=booking_id, user=request.user)
    else:
        return redirect('user_profile')

    booking.delete()  # Удаляем бронь
    return redirect('user_profile')  # Перенаправляем в личный кабинет


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Хешируем пароль
            user.save()
            UserProfile.objects.create(user=user)  # Создаём профиль
            login(request, user)  # Авторизуем пользователя после регистрации
            return redirect('user_profile')
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})


