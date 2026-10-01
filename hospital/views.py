
from django.shortcuts import render
from .models import Doctor,Category,DoctorAvailability,Patient,Appointment

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
    category = Category.objects.get(id=category_id)
    doctors = Doctor.objects.filter(category=category)
    return render(request, "category_doctors.html", {
    "category": category,
    "doctors": doctors
})

# ///////

def book_appointment(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)

    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        is_available=True
    ).order_by("date", "start_time")

    patients = Patient.objects.filter(is_active=True)

    if request.method == "POST":
        patient_id = request.POST["patient"]
        availability_id = request.POST["availability"]
        reason = request.POST["reason"]

        patient = Patient.objects.get(id=patient_id)

        availability = DoctorAvailability.objects.get(
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