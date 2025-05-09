from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.jpg')
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)  # Дата рождения
    nationality = models.CharField(max_length=50, blank=True, null=True)  # Гражданство
    passport_id = models.CharField(max_length=20, blank=True, null=True)  # ID паспорта

    def __str__(self):
        return self.user.username

