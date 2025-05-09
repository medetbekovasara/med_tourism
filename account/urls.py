from django.urls import path
from django.contrib.auth import views as auth_views
from .views import user_profile, edit_profile, register, cancel_booking

urlpatterns = [
    path('profile/', user_profile, name='user_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/cancel/<str:booking_type>/<int:booking_id>/', cancel_booking, name='cancel_booking'),

]

