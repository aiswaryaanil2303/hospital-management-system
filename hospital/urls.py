from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("doctors/<int:doctor_id>/", views.doctor_detail, name="doctor_detail"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<int:category_id>/", views.category_doctors, name="category_doctors"),
    path("appointments/book/<int:doctor_id>/", views.book_appointment, name="book_appointment"),
    path("appointments/", views.appointment_list, name="appointment_list"),
    path(
    "doctor/<int:doctor_id>/dashboard/",
    views.doctor_dashboard,
    name="doctor_dashboard",
),

path(
    "appointments/<int:appointment_id>/prescription/",
    views.add_prescription,
    name="add_prescription"
),

path(
    "patient/<int:patient_id>/prescriptions/",
    views.view_prescriptions,
    name="view_prescriptions"
),


path("patient/login/", views.patient_login, name="patient_login"),
path("patient/verify-otp/", views.verify_otp, name="verify_otp"),
] 