from django.contrib.auth.models import User
from django.db import models

class Clinic(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    description = models.TextField()
    photo = models.ImageField(upload_to='clinics/')
    specializations = models.TextField()

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    experience = models.IntegerField()
    photo = models.ImageField(upload_to='doctors/')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    available_dates = models.TextField()

    def __str__(self):
        return self.name


class ClinicBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)  # 🔴 Добавляем лечащего врача
    department = models.CharField(max_length=255)  # 🔴 Отделение клиники
    start_date = models.DateField()  # 🔴 Дата начала брони
    end_date = models.DateField()  # 🔴 Дата окончания брони
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'В ожидании'), ('confirmed', 'Подтверждено'), ('canceled', 'Отменено')],
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - {self.clinic.name} ({self.department}) - {self.start_date} to {self.end_date}"

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='hotels/', blank=True, null=True)

    def __str__(self):
        return self.name


class HotelBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guests = models.IntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'В ожидании'), ('confirmed', 'Подтверждено'), ('canceled', 'Отменено')],
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} - {self.check_in_date}"



class ConsultationBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'В ожидании'), ('confirmed', 'Подтверждено'), ('canceled', 'Отменено')],
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - {self.doctor.name} - {self.date}"

