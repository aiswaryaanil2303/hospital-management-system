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
] 