from django import forms
from .models import Appointment


class BookAppointmentForm(forms.Form):
    """Step 1: patient picks a date. Step 2: slots reload via AJAX."""
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    slot_time = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                     'placeholder': 'Brief reason for this visit...'})
    )

    def __init__(self, *args, slots=None, **kwargs):
        super().__init__(*args, **kwargs)
        if slots:
            self.fields['slot_time'].choices = [
                (s['time'], f"{s['time']} {'✓ Available' if s['available'] else '✗ Booked'}")
                for s in slots if s['available']
            ]
        else:
            self.fields['slot_time'].choices = [('', '— Select a date first —')]
