import random
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages

from .models import (
    Doctor,
    Category,
    DoctorAvailability,
    Patient,
    Appointment,
    Prescription,
)

# Create your views here.

def home(request):
    return render(request, "home.html")


def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, "doctor_list.html", {"doctors": doctors})


def doctor_detail(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    return render(request, "doctor_detail.html", {"doctor": doctor})

def category_list(request):
    categories = Category.objects.all()
    return render(request, "categories.html", {"categories": categories})



def category_doctors(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    doctors = Doctor.objects.filter(category=category, is_active=True)
    return render(request, "category_doctors.html", {
        "category": category,
        "doctors": doctors
    })


# ///////

def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        is_available=True
    ).order_by("date", "start_time")

    patients = Patient.objects.filter(is_active=True)

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        availability_id = request.POST.get("availability")
        reason = request.POST.get("reason", "")

        patient = get_object_or_404(Patient, id=patient_id)

        availability = get_object_or_404(
            DoctorAvailability,
            id=availability_id,
            doctor=doctor,
            is_available=True
        )

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=availability.date,
            time=availability.start_time,
            reason=reason
        )
        availability.is_available = False
        availability.save()
        messages.success(request, f"Appointment booked successfully with {doctor.name}!")
        return redirect("appointment_list")

    return render(request, "book_appointment.html", {
        "doctor": doctor,
        "availabilities": availabilities,
        "patients": patients
    })



def appointment_list(request):
    appointments = Appointment.objects.all().order_by("-created_at")

    return render(request, "appointment_list.html", {
        "appointments": appointments
    })


# -----get the objects if get otherwise error ////////

def doctor_dashboard(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).order_by("date", "time")

    return render(request, "doctor_dashboard.html", {
        "doctor": doctor,
        "appointments": appointments,
    })

# ////////// for add prescription/////------


def add_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        medicine = request.POST.get("medicine")
        dosage = request.POST.get("dosage")
        notes = request.POST.get("notes")
        follow_up_date = request.POST.get("follow_up_date") or None

        prescription = Prescription(
            appointment=appointment,
            medicine=medicine,
            dosage=dosage,
            notes=notes,
            follow_up_date=follow_up_date
        )
        prescription.save()

    return render(request, "prescription_add.html", {
        "appointment": appointment
    })


    # ///////# display to patient/////////////


def view_prescriptions(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    )

    return render(request, "prescriptions.html", {
        "prescriptions": prescriptions
    })




def patient_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        try:
            patient = Patient.objects.get(email=email, is_active=True)

            otp = str(random.randint(100000, 999999))

            patient.otp = otp
            patient.otp_created_at = timezone.now()
            patient.save()

            try:
                send_mail(
                    "Hospital OTP",
                    "Your OTP is " + otp,
                    None,
                    [email],
                    fail_silently=True,
                )
            except Exception:
                pass

            request.session["patient_email"] = email
            return redirect("verify_otp")

        except Patient.DoesNotExist:
            messages.error(request, "Patient not found.")

    return render(request, "patient_login.html")


def verify_otp(request):
    if request.method == "POST":
        email = request.session.get("patient_email")
        otp = request.POST.get("otp", "").strip()

        try:
            patient = Patient.objects.get(email=email)

            if (
                patient.otp == otp
                and patient.otp_created_at
                and timezone.now() - patient.otp_created_at
                < timedelta(minutes=5)
            ):
                patient.otp = None
                patient.otp_created_at = None
                patient.save()

                request.session["patient_id"] = patient.id
                return redirect("home")

            else:
                messages.error(request, "Invalid or expired OTP.")

        except Patient.DoesNotExist:
            messages.error(request, "Patient not found.")

    return render(request, "verify_otp.html")

