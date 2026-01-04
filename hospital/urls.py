from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    # path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patient-distribution/', views.patient_distribution, name='patient_distribution'),
    path('graph/', views.doctor_patient_graph, name='doctor_patient_graph'),
    path('graph/data/', views.doctor_patient_graph_data, name='doctor_patient_graph_data'),

    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('remove-doctor/', views.remove_doctor, name='remove_doctor'),

    path('add-patient/', views.add_patient, name='add_patient'),
    path('remove-patient/', views.remove_patient, name='remove_patient'),

    path('add-consent/', views.add_consent, name='add_consent'),

    path('login/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('add-appointment/', views.add_appointment, name='add_appointment'),
    path("register-doctor/", views.doctor_register, name="doctor_register"),
    path("register-patient/", views.patient_register, name="patient_register"),
    path("patient/dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path('patient/<int:patient_id>/update-history/', views.update_medical_history, name='update_medical_history'),
    path("appointments-json/", views.appointments_json, name="appointments_json"),
]



