
import random
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from .models import (
    Doctor,
    Category,
    DoctorAvailability,
    Patient,
    Appointment,
    Prescription,
)


def home(request):
    return render(request, "home.html")


def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True)
    return render(request, "doctor_list.html", {"doctors": doctors})


def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)
    return render(request, "doctor_detail.html", {"doctor": doctor})


def category_list(request):
    categories = Category.objects.all()
    return render(request, "categories.html", {"categories": categories})


def category_doctors(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    doctors = Doctor.objects.filter(category=category, is_active=True)

    return render(request, "category_doctors.html", {
        "category": category,
        "doctors": doctors,
    })


def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)

    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        is_available=True,
        date__gte=timezone.localdate(),
    ).order_by("date", "start_time")

    patients = Patient.objects.filter(is_active=True)

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        availability_id = request.POST.get("availability")
        reason = request.POST.get("reason", "").strip()

        if not patient_id or not availability_id or not reason:
            messages.error(request, "Please complete all fields.")
            return render(request, "book_appointment.html", {
                "doctor": doctor,
                "availabilities": availabilities,
                "patients": patients,
            })

        patient = get_object_or_404(
            Patient, id=patient_id, is_active=True
        )

        availability = get_object_or_404(
            DoctorAvailability,
            id=availability_id,
            doctor=doctor,
            is_available=True,
            date__gte=timezone.localdate(),
        )

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=availability.date,
            time=availability.start_time,
            reason=reason,
        )

        availability.is_available = False
        availability.save(update_fields=["is_available"])

        messages.success(
            request,
            f"Appointment booked successfully with {doctor.name}!",
        )
        return redirect("appointment_list")

    return render(request, "book_appointment.html", {
        "doctor": doctor,
        "availabilities": availabilities,
        "patients": patients,
    })


def appointment_list(request):
    appointments = Appointment.objects.all().order_by("-created_at")
    return render(request, "appointment_list.html", {
        "appointments": appointments,
    })


def doctor_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        try:
            doctor = Doctor.objects.get(
                username=username,
                is_active=True,
            )
        except Doctor.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return render(request, "doctor_login.html")

        if doctor.password and check_password(password, doctor.password):
            request.session.cycle_key()
            request.session["doctor_id"] = doctor.id
            return redirect("doctor_dashboard", doctor_id=doctor.id)

        messages.error(request, "Invalid username or password.")

    return render(request, "doctor_login.html")


def doctor_logout(request):
    request.session.pop("doctor_id", None)
    messages.success(request, "You have logged out successfully.")
    return redirect("home")


def doctor_dashboard(request, doctor_id):
    logged_in_doctor_id = request.session.get("doctor_id")

    if not logged_in_doctor_id:
        messages.error(request, "Please log in first.")
        return redirect("doctor_login")

    if logged_in_doctor_id != doctor_id:
        messages.error(
            request,
            "You cannot access another doctor's dashboard.",
        )
        return redirect("home")

    doctor = get_object_or_404(
        Doctor,
        id=logged_in_doctor_id,
        is_active=True,
    )

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).order_by("date", "time")

    return render(request, "doctor_dashboard.html", {
        "doctor": doctor,
        "appointments": appointments,
    })


def add_prescription(request, appointment_id):
    logged_in_doctor_id = request.session.get("doctor_id")

    if not logged_in_doctor_id:
        messages.error(request, "Please log in first.")
        return redirect("doctor_login")

    doctor = get_object_or_404(
        Doctor,
        id=logged_in_doctor_id,
        is_active=True,
    )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=doctor,
    )

    if request.method == "POST":
        medicine = request.POST.get("medicine", "").strip()
        dosage = request.POST.get("dosage", "").strip()
        notes = request.POST.get("notes", "").strip()
        follow_up_date = request.POST.get("follow_up_date") or None

        if not medicine or not dosage:
            messages.error(request, "Medicine and dosage are required.")
        else:
            Prescription.objects.create(
                appointment=appointment,
                medicine=medicine,
                dosage=dosage,
                notes=notes,
                follow_up_date=follow_up_date,
            )

            messages.success(request, "Prescription added successfully.")
            return redirect("doctor_dashboard", doctor_id=doctor.id)

    return render(request, "prescription_add.html", {
        "appointment": appointment,
    })


def view_prescriptions(request, patient_id):
    logged_in_patient_id = request.session.get("patient_id")

    if not logged_in_patient_id:
        messages.error(request, "Please log in to view prescriptions.")
        return redirect("patient_login")

    if logged_in_patient_id != patient_id:
        messages.error(
            request,
            "You cannot view another patient's prescriptions.",
        )
        return redirect("home")

    patient = get_object_or_404(
        Patient,
        id=logged_in_patient_id,
        is_active=True,
    )

    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    ).select_related("appointment", "appointment__doctor")

    return render(request, "prescriptions.html", {
        "prescriptions": prescriptions,
    })


def patient_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        try:
            patient = Patient.objects.get(
                email__iexact=email,
                is_active=True,
            )
        except Patient.DoesNotExist:
            messages.error(request, "Patient not found or inactive.")
            return render(request, "patient_login.html")

        otp = str(random.randint(100000, 999999))

        try:
            send_mail(
                "Hospital OTP",
                f"Your OTP is {otp}. It is valid for 5 minutes.",
                None,
                [patient.email],
                fail_silently=False,
            )
        except Exception:
            messages.error(
                request,
                "Unable to send OTP. Please try again.",
            )
            return render(request, "patient_login.html")

        patient.otp = otp
        patient.otp_created_at = timezone.now()
        patient.save(update_fields=["otp", "otp_created_at"])

        request.session["patient_email"] = patient.email
        return redirect("verify_otp")

    return render(request, "patient_login.html")


def verify_otp(request):
    email = request.session.get("patient_email")

    if not email:
        messages.error(request, "Please log in first.")
        return redirect("patient_login")

    if request.method == "POST":
        otp = request.POST.get("otp", "").strip()

        try:
            patient = Patient.objects.get(
                email=email,
                is_active=True,
            )
        except Patient.DoesNotExist:
            request.session.pop("patient_email", None)
            messages.error(request, "Patient not found or inactive.")
            return redirect("patient_login")

        if (
            patient.otp
            and patient.otp == otp
            and patient.otp_created_at
            and timezone.now() - patient.otp_created_at
            < timedelta(minutes=5)
        ):
            patient.otp = None
            patient.otp_created_at = None
            patient.save(update_fields=["otp", "otp_created_at"])

            request.session.cycle_key()
            request.session["patient_id"] = patient.id
            request.session.pop("patient_email", None)

            return redirect("home")

        messages.error(request, "Invalid or expired OTP.")

    return render(request, "verify_otp.html")


def patient_logout(request):
    request.session.pop("patient_id", None)
    request.session.pop("patient_email", None)
    messages.success(request, "You have logged out successfully.")
    return redirect("home")

