from .models import AccessLog, Doctor

def log_action(request, patient, action):
    try:
        doctor = Doctor.objects.get(user=request.user)
        AccessLog.objects.create(
            doctor=doctor,
            patient=patient,
            action=action
        )
    except Doctor.DoesNotExist:
        AccessLog.objects.create(
            user=request.user,
            patient=patient,
            action=action
        )