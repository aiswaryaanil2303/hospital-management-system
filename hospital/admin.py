from django.contrib import admin
from .models import Category, Doctor,Patient,DoctorAvailability,Appointment,Prescription

admin.site.register(Doctor)
admin.site.register(Category)
admin.site.register(Patient)
admin.site.register(DoctorAvailability)
admin.site.register(Appointment) 
admin.site.register(Prescription)