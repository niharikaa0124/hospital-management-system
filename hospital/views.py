from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse

from .models import Patient, Doctor, Consent, AccessLog
from .forms import DoctorForm, PatientForm, ConsentForm, DoctorRegisterForm, PatientRegistrationForm
from .models import Appointment
from .utils import log_action

def is_doctor(user):
    return Doctor.objects.filter(user=user).exists()

def is_admin(user):
    return user.is_superuser


# Dashboard
@login_required
def dashboard(request):
    patients = Patient.objects.all()

    # Bar Chart Data
    chart_data = []
    for doctor in Doctor.objects.all():
        patients_with_consent = Patient.objects.filter(consent__doctor=doctor, consent__granted=True)
        chart_data.append({
            'doctor': doctor.name,
            'patients': list(patients_with_consent.values('id', 'name'))
        })

    # Graph Data
    nodes = []
    edges = []
    for doctor in Doctor.objects.all():
        nodes.append({
            'data': {'id': f'doctor_{doctor.id}', 'label': doctor.name, 'type': 'doctor'}
        })

        patient_list = Patient.objects.filter(consent__doctor=doctor, consent__granted=True)
        for patient in patient_list:
            if not any(n['data']['id'] == f'patient_{patient.id}' for n in nodes):
                nodes.append({
                    'data': {'id': f'patient_{patient.id}', 'label': patient.name, 'type': 'patient'}
                })

            edges.append({
                'data': {'source': f'patient_{patient.id}', 'target': f'doctor_{doctor.id}'}
            })

    graph_data = {'nodes': nodes, 'edges': edges}

    
    doctor_user = Doctor.objects.filter(user=request.user).exists()

    doctor_patients = []
    if doctor_user:
        doctor_patients = Patient.objects.filter(consent__doctor=doctor_user, consent__granted=True)

    access_logs = AccessLog.objects.select_related("user", "doctor", "patient").order_by("-timestamp")

    return render(request, 'hospital/dashboard.html', {
            'patients': patients,
            'chart_data': chart_data,
            'graph_data': graph_data,
            'add_doctor_form': DoctorForm(),
            'add_patient_form': PatientForm(),
            'consent_form': ConsentForm(),
            'doctors': Doctor.objects.all(),
            'doctor_user': doctor_user, 
            'doctor_patients': doctor_patients,
            "access_logs": access_logs
    })



#  Patient Detail
@login_required
def patient_detail(request, patient_id):
    patient = Patient.objects.get(id=patient_id)

    AccessLog.objects.create(user=request.user, patient=patient, action="Viewed patient record")

    consents = Consent.objects.filter(patient=patient, doctor__name=request.user.username, granted=True)
    medical_history = patient.get_medical_history() if consents.exists() else "Access Denied"

    return render(request, 'hospital/patient_detail.html', {
        'patient': patient,
        'medical_history': medical_history
    })


#  Bar chart page
def patient_distribution(request):
    data = []
    for doctor in Doctor.objects.all():
        patients = Patient.objects.filter(consent__doctor=doctor, consent__granted=True)
        data.append({
            'doctor': doctor.name,
            'patients': list(patients.values('id', 'name'))
        })
    return render(request, 'hospital/patient_distribution.html', {'data': data})


#  Graph HTML page
def doctor_patient_graph(request):
    return render(request, 'hospital/doctor_patient_graph.html')


#  Graph Data API
def doctor_patient_graph_data(request):
    elements = []

    doctors = Doctor.objects.all()
    for d in doctors:
        elements.append({
            'data': {
                'id': f'doctor_{d.id}',
                'label': f"{d.name} ({d.specialization})",
                'type': 'doctor'
            }
        })

    for p in Patient.objects.all():
        consents = Consent.objects.filter(patient=p, granted=True)
        for c in consents:
            elements.append({
                'data': {
                    'id': f'patient_{p.id}',
                    'label': p.name,
                    'type': 'patient'
                }
            })
            elements.append({
                'data': {
                    'source': f'patient_{p.id}',
                    'target': f'doctor_{c.doctor.id}'
                }
            })

    return JsonResponse(elements, safe=False)


#  Custom Login
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            #  ROLE-BASED REDIRECTION
            if user.is_superuser:
                return redirect("dashboard")  # Admin dashboard

            #  Doctor user has OneToOne relation: doctor.user → User
            if hasattr(user, "doctor"):
                return redirect("dashboard")  # Doctor dashboard (same UI)

            #  Patient user has OneToOne relation: patient.user → User
            if hasattr(user, "patient"):
                return redirect("patient_dashboard")  # Redirect patient to patient dashboard

            # Default fallback
            return redirect("dashboard")

        messages.error(request, "Invalid username or password")

    return render(request, "hospital/login.html")

# Add Doctor
@user_passes_test(is_admin)
def add_doctor(request):
    if request.method == "POST":
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save()

            AccessLog.objects.create(
                user=request.user,
                action=f"Added Doctor {doctor.name}"
            )

            return redirect("dashboard")

    else:
        form = DoctorForm()

    return render(request, "hospital/add_doctor_form.html", {"form": form})





#  Remove Doctor
@user_passes_test(is_admin)
def remove_doctor(request):
    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        doctor = Doctor.objects.filter(id=doctor_id).first()

        if doctor:
            # Delete the doctor
            doctor_name = doctor.name
            doctor.delete()

            #  Log admin action
            AccessLog.objects.create(
                user=request.user,
                action=f"Removed Doctor {doctor_name}"
            )

        return redirect("dashboard")

    # GET request → load doctor list
    doctors = Doctor.objects.all()
    return render(request, "hospital/remove_doctor.html", {"doctors": doctors})

#  Add Patient
@user_passes_test(is_admin)
def add_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()

            # Log ONLY when a new patient is really added
            log_action(request, patient, "Added New Patient")

            return redirect('dashboard')
    else:
        form = PatientForm()

    return render(request, "hospital/add_patient.html", {"form": form})


# Remove Patient
@user_passes_test(is_admin)
def remove_patient(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        patient = Patient.objects.filter(id=patient_id).first()

        if patient:
            patient_name = patient.name
            patient.delete()

            #  Admin action log
            AccessLog.objects.create(
                user=request.user,
                action=f"Removed Patient {patient_name}"
            )

        return redirect("dashboard")

    # GET request → Show patient list
    patients = Patient.objects.all()
    return render(request, "hospital/remove_patient.html", {"patients": patients})

@login_required
@user_passes_test(is_doctor)
def add_appointment(request):
    doctor = Doctor.objects.get(user=request.user)

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        date = request.POST.get("appointment_date")
        notes = request.POST.get("notes")

        patient = Patient.objects.filter(id=patient_id).first()
        if not patient:
            messages.error(request, "Patient not found.")
            return redirect("dashboard")

        # Create the appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=date,
            notes=notes
        )

        # Log doctor action
        AccessLog.objects.create(
            doctor=doctor,
            patient=patient,
            action=f"Created Appointment on {date}"
        )

        messages.success(request, "Appointment added successfully.")
        return redirect("dashboard")

    # GET request (form is inside dashboard)
    return redirect("dashboard")


#  Add consent
@user_passes_test(is_admin)
def add_consent(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        granted = request.POST.get("granted") == "on"

        patient = Patient.objects.get(id=patient_id)
        doctor = Doctor.objects.get(id=doctor_id)

        # Create or update consent (this is enough)
        consent, created = Consent.objects.update_or_create(
            patient=patient,
            doctor=doctor,
            defaults={"granted": granted}
        )

        # Log admin action
        action_msg = f"Consent {'Granted' if granted else 'Revoked'} to  {doctor.name}"
        log_action(request, patient, action_msg)

        return redirect("dashboard")

    return redirect("dashboard")


from django.contrib.auth.models import User
from django.contrib.auth import login

def doctor_register(request):
    if request.method == "POST":
        form = DoctorRegisterForm(request.POST)

        if form.is_valid():
            doctor = form.cleaned_data["doctor"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            #  Prevent duplicate usernames
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return render(request, "hospital/doctor_register.html", {"form": form})

            #  Prevent linking if doctor already has a user
            if doctor.user:
                messages.error(request, "This doctor already has a registered account.")
                return render(request, "hospital/doctor_register.html", {"form": form})

            #  Create user
            user = User.objects.create_user(username=username, password=password)

            #  Link doctor to user
            doctor.user = user
            doctor.save()

            #  Log registration
            AccessLog.objects.create(
                user=user,
                action=f"Doctor account registered for {doctor.name}",
                patient=None  # No patient involved
            )

            #  Auto login
            login(request, user)

            return redirect("dashboard")
    else:
        form = DoctorRegisterForm()

    return render(request, "hospital/doctor_register.html", {"form": form})


def patient_register(request):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            #  Prevent duplicate usernames
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return render(request, "hospital/patient_register.html", {"form": form})

            #  Create user
            user = User.objects.create_user(username=username, password=password)

            #  Create patient model linked to user
            patient = form.save(commit=False)
            patient.user = user
            patient.save()

            #  Access Log
            AccessLog.objects.create(
                user=user,
                patient=patient,
                action="Patient Registered"
            )

            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")

    else:
        form = PatientRegistrationForm()

    return render(request, "hospital/patient_register.html", {"form": form})



from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient, Appointment, Consent


@login_required
def patient_dashboard(request):
    # Ensure logged-in user is actually a patient
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "You are not registered as a patient.")
        return redirect("dashboard")  # fallback for doctor/admin

    appointments = Appointment.objects.filter(patient=patient).order_by("appointment_date")
    consents = Consent.objects.filter(patient=patient)

    return render(request, "hospital/patient_dashboard.html", {
        "patient": patient,
        "appointments": appointments,
        "consents": consents,
        "medical_history": patient.get_medical_history(),
    })

from .forms import DoctorMedicalHistoryForm
from django.shortcuts import get_object_or_404

@login_required
@user_passes_test(is_doctor)
def update_medical_history(request, patient_id):
    doctor = get_object_or_404(Doctor, user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)

    #  Check if doctor has consent
    if not Consent.objects.filter(doctor=doctor, patient=patient, granted=True).exists():
        messages.error(request, "You do not have consent to update this patient's medical history.")
        return redirect("dashboard")

    if request.method == "POST":
        form = DoctorMedicalHistoryForm(request.POST, instance=patient)

        if form.is_valid():
            medical_history_text = form.cleaned_data['medical_history']

            #  Encrypt + Save using your model's method
            patient.set_medical_history(medical_history_text)
            patient.save()

            #  LOG ACTION
            AccessLog.objects.create(
                doctor=doctor,
                patient=patient,
                action="Updated Medical History"
            )

            messages.success(request, "Medical history updated successfully.")
            return redirect("dashboard")

    else:
        #  Prefill decrypted medical history
        initial_data = {'medical_history': patient.get_medical_history()}
        form = DoctorMedicalHistoryForm(initial=initial_data)

        #  OPTIONAL: log that doctor viewed medical history edit page
        AccessLog.objects.create(
            doctor=doctor,
            patient=patient,
            action="Viewed Medical History Update Page"
        )

    return render(request, "hospital/update_medical_history.html", {
        "form": form,
        "patient": patient
    })

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def appointments_json(request):
    doctor = Doctor.objects.get(user=request.user)

    appointments = Appointment.objects.filter(doctor=doctor)

    data = []
    for a in appointments:
        data.append({
            "title": f"{a.patient.name}",
            "start": a.appointment_date.isoformat(),
            "description": a.notes or ""
        })

    return JsonResponse(data, safe=False)
