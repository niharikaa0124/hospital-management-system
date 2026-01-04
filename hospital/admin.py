from django.contrib import admin
from .models import Patient, Doctor, Consent, AccessLog

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'contact')
    search_fields = ('name', 'contact')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization')

@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'granted', 'updated_at')
    list_filter = ('granted',)

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'patient', 'doctor', 'user', 'timestamp')
    search_fields = ('patient__name', 'doctor__name', 'user__username', 'action')
    list_filter = ('timestamp',)

from django.urls import path
from django.shortcuts import render

class MyAdminSite(admin.AdminSite):
    site_header = "GuardianDB Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Prepare data: which patients are under which doctor
        data = []
        doctors = Doctor.objects.all()
        for doctor in doctors:
            patients = [consent.patient.name for consent in Consent.objects.filter(doctor=doctor, granted=True)]
            data.append({'doctor': doctor.name, 'patients': patients})
        context = dict(
            self.each_context(request),
            data=data
        )
        return render(request, "admin/hospital/dashboard.html", context)


# Replace default admin with custom admin
admin_site = MyAdminSite(name='myadmin')

# Register your models to the custom admin site
admin_site.register(Patient, PatientAdmin)
admin_site.register(Doctor, DoctorAdmin)
admin_site.register(Consent, ConsentAdmin)
admin_site.register(AccessLog, AccessLogAdmin)
