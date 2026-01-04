from django import forms
from .models import Consent, Doctor, Patient
from .models import Appointment
from django.contrib.auth.models import User

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["name", "specialization"]

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["name", "age", "address", "contact"]
class ConsentForm(forms.ModelForm):
    class Meta:
        model = Consent
        fields = ['patient', 'doctor', 'granted']

    granted = forms.BooleanField(
        required=False,
        label="Consent Granted?",
        help_text="Tick to grant consent, untick to revoke."
    )

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "appointment_date", "notes"]
        widgets = {
            "appointment_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class DoctorRegisterForm(forms.Form):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(user__isnull=True),
        label="Select Your Name"
    )
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

from .models import EncryptionHelper


class PatientRegistrationForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    age = forms.IntegerField()
    address = forms.CharField(required=False)
    contact = forms.CharField(max_length=15)

    def save(self):
        # Create user first
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"]
        )

        # Create patient linked to user
        patient = Patient.objects.create(
            user=user,
            name=self.cleaned_data["name"],
            age=self.cleaned_data["age"],
            address=self.cleaned_data.get("address", ""),
            contact=self.cleaned_data["contact"],
            encrypted_medical_history=EncryptionHelper.encrypt("No medical history yet.")
        )
        return patient

from django import forms
class DoctorMedicalHistoryForm(forms.ModelForm):
    medical_history = forms.CharField(
        widget=forms.Textarea,
        label="Medical History",
        required=True
    )

    class Meta:
        model = Patient
        fields = []