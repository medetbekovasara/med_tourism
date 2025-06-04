from .models import *
from datetime import datetime
from .models import ConsultationBooking
from django import forms
from .models import HotelBooking
from datetime import date

class ClinicBookingForm(forms.ModelForm):
    class Meta:
        model = ClinicBooking
        fields = ['clinic', 'doctor', 'department', 'start_date', 'end_date']
        widgets = {
            'clinic': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название отделения',
                'required': True
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
        }
        labels = {
            'clinic': 'Клиника',
            'doctor': 'Врач',
            'department': 'Отделение',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
        }

    def __init__(self, *args, **kwargs):
        clinic_id = kwargs.pop('clinic_id', None)  # <-- добавляем поддержку clinic_id
        super().__init__(*args, **kwargs)

        self.fields['clinic'].queryset = Clinic.objects.all()
        self.fields['clinic'].empty_label = "Выберите клинику"
        self.fields['doctor'].empty_label = "Выберите врача"

        # Фильтрация списка врачей
        if 'clinic' in self.data:
            try:
                clinic_id = int(self.data.get('clinic'))
            except (ValueError, TypeError):
                clinic_id = None

        if clinic_id:
            self.fields['doctor'].queryset = Doctor.objects.filter(clinic_id=clinic_id)
        else:
            self.fields['doctor'].queryset = Doctor.objects.none()


    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("Дата окончания не может быть раньше даты начала.")

        return cleaned_data


class ConsultationBookingForm(forms.ModelForm):
    class Meta:
        model = ConsultationBooking
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

        self.fields['time'] = forms.ChoiceField(
            choices=[],
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=True,
            label="Время"
        )

        # Пробуем получить дату из self.data или из initial (если это GET)
        date_str = self.data.get('date') or self.initial.get('date')

        if date_str and self.doctor:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                # Все часы: 09:00 – 17:00
                hours = [f"{h:02d}:00" for h in range(9, 18)]

                # Занятые у врача
                taken_times = ConsultationBooking.objects.filter(
                    doctor=self.doctor,
                    date=selected_date
                ).values_list('time', flat=True)
                taken_strings = [t.strftime('%H:%M') for t in taken_times]

                # Доступные
                available = [(t, t) for t in hours if t not in taken_strings]

                self.fields['time'].choices = available

            except Exception as e:
                print("Ошибка генерации времён:", e)


class HotelBookingForm(forms.ModelForm):
    class Meta:
        model = HotelBooking
        fields = ['check_in_date', 'check_out_date', 'guests']

    def clean_check_in_date(self):
        check_in = self.cleaned_data.get('check_in_date')
        if check_in < date.today():
            raise forms.ValidationError("Нельзя выбрать прошедшую дату заезда.")
        return check_in

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')

        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Дата выезда должна быть позже даты заезда.")



