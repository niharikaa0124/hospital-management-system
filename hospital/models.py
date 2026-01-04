from django.db import models
from cryptography.fernet import Fernet
from django.contrib.auth.models import User

# Step 1: Encryption helper
class EncryptionHelper:
    # FIXED key — generate once and reuse
    # Example: Fernet.generate_key() -> store this in a variable or .env
    key = b'go2vz-2S-EklURltX8XkusMLnegRlCTBBbXg8_bhrJk='
    fernet = Fernet(key)

    @staticmethod
    def encrypt(data):
        return EncryptionHelper.fernet.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt(data):
        return EncryptionHelper.fernet.decrypt(data.encode()).decode()

from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    address = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=15)
    encrypted_medical_history = models.TextField()

    def set_medical_history(self, text):
        self.encrypted_medical_history = EncryptionHelper.encrypt(text)

    def get_medical_history(self):
        return EncryptionHelper.decrypt(self.encrypted_medical_history)


# Step 3: Doctor model
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.specialization})"



# Step 4: Consent model
class Consent(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    granted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Granted" if self.granted else "Revoked"
        return f"{self.patient.name} → {self.doctor.name} ({status})"


# Step 5: Access log model
class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        actor = (
            self.user.username if self.user
            else self.doctor.name if self.doctor
            else "System"
        )

        target = self.patient.name if self.patient else "N/A"

        return f"{actor} -> {self.action} ({target}) at {self.timestamp}"


# Step 6: Appointment model
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment: {self.patient.name} with {self.doctor.name} on {self.appointment_date}"

