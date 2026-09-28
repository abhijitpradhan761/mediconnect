from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile


class PatientRegistrationForm(forms.ModelForm):
    """
    Registration form for new Patients.
    Creates User account with PATIENT role and associated PatientProfile in a single atomic transaction.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        min_length=8,
        help_text='At least 8 characters.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        help_text='Repeat password to confirm.'
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=PatientProfile.Gender.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    blood_group = forms.ChoiceField(
        choices=[('', 'Select Blood Group (Optional)')] + list(PatientProfile.BloodGroup.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your home address'})
    )
    emergency_contact_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'})
    )
    emergency_contact_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1-555-0100'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1-555-0123'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PATIENT
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender'),
                blood_group=self.cleaned_data.get('blood_group') or None,
                address=self.cleaned_data.get('address', ''),
                emergency_contact_name=self.cleaned_data.get('emergency_contact_name', ''),
                emergency_contact_phone=self.cleaned_data.get('emergency_contact_phone', ''),
            )
        return user


class DoctorRegistrationForm(forms.ModelForm):
    """
    Registration form for Medical Practitioners.
    Creates User with DOCTOR role and unapproved DoctorProfile awaiting administrator review.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    specialization = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cardiology, Pediatrics'})
    )
    qualification = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MBBS, MD (Internal Medicine)'})
    )
    license_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medical Registration / License ID'})
    )
    experience_years = forms.IntegerField(
        min_value=0,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    consultation_fee = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        initial=50.00,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief clinical background...'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'doctor_username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'dr.smith@hospital.org'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1-555-0144'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_license_number(self):
        license_num = self.cleaned_data.get('license_number')
        if license_num and DoctorProfile.objects.filter(license_number__iexact=license_num).exists():
            raise ValidationError("A doctor profile with this license number has already been registered.")
        return license_num

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.DOCTOR
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                qualification=self.cleaned_data['qualification'],
                license_number=self.cleaned_data['license_number'],
                experience_years=self.cleaned_data['experience_years'],
                consultation_fee=self.cleaned_data['consultation_fee'],
                bio=self.cleaned_data.get('bio', ''),
                is_approved=False,  # Requires Admin approval
            )
        return user


class UserLoginForm(forms.Form):
    """
    Flexible login form accepting either Username or Email Address along with Password.
    """
    username_or_email = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email', 'autofocus': True}),
        label="Username or Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        label="Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if username_or_email and password:
            # First attempt direct authentication with username
            user = authenticate(username=username_or_email, password=password)
            if user is None:
                # If username failed, search for matching email
                try:
                    user_by_email = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(username=user_by_email.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is None:
                raise ValidationError("Invalid login credentials. Please check your username/email and password.")
            if not user.is_active:
                raise ValidationError("This account has been deactivated. Please contact support.")

            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)
