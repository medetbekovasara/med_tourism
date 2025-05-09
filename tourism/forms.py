from .models import ClinicBooking, HotelBooking, ConsultationBooking
from django import forms
from .models import ClinicBooking


class ClinicBookingForm(forms.ModelForm):
    department = forms.ChoiceField(
        choices=[
            ('Кардиология', 'Кардиология'),
            ('Ортопедия', 'Ортопедия'),
            ('Неврология', 'Неврология'),
            ('Онкология', 'Онкология'),
            ('Гастроэнтерология', 'Гастроэнтерология')
        ],
        label="Отделение"
    )

    class Meta:
        model = ClinicBooking
        fields = ['clinic', 'doctor', 'department', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ConsultationBookingForm(forms.ModelForm):
    class Meta:
        model = ConsultationBooking
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }


class HotelBookingForm(forms.ModelForm):
    class Meta:
        model = HotelBooking
        fields = ['check_in_date', 'check_out_date', 'guests']


