from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from hospital.models import Category, Doctor, DoctorAvailability

class Command(BaseCommand):
    help = "Seeds initial categories, doctors, and doctor availability"

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        categories_data = [
            ("Cardiology", "Specializes in heart disorders and cardiovascular wellness."),
            ("Neurology", "Specializes in nervous system and neurological care."),
            ("Pediatrics", "Comprehensive medical care for infants, children, and adolescents."),
            ("Orthopedics", "Diagnosis and treatment of musculoskeletal conditions."),
            ("General Medicine", "Comprehensive adult healthcare and preventive medicine."),
        ]

        categories = {}
        for name, desc in categories_data:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": desc}
            )
            categories[name] = cat
            if created:
                self.stdout.write(f"Created category: {name}")

        cardio = categories.get("Cardiology")
        if cardio:
            doctor, created = Doctor.objects.get_or_create(
                email="dr.aiswarya@hospital.com",
                defaults={
                    "name": "Dr. Aiswarya Anil",
                    "username": "draanils",
                    "category": cardio,
                    "photo": "doctors/doctor-img1.jpg",
                    "experience": 8,
                    "phone": "9876543210",
                    "about": "Senior Consultant Cardiologist with over 8 years of clinical experience.",
                    "is_active": True,
                }
            )
            if created:
                self.stdout.write(f"Created doctor: {doctor.name}")

            neuro = categories.get("Neurology")
            if neuro:
                doc2, created2 = Doctor.objects.get_or_create(
                    email="dr.smith@hospital.com",
                    defaults={
                        "name": "Dr. John Smith",
                        "username": "drjsmith",
                        "category": neuro,
                        "photo": "doctors/doctor-img1.jpg",
                        "experience": 10,
                        "phone": "9876543211",
                        "about": "Senior Neurologist specializing in brain and nervous system care.",
                        "is_active": True,
                    }
                )
                if created2:
                    self.stdout.write(f"Created doctor: {doc2.name}")

            today = date.today()
            for offset in range(1, 4):
                avail_date = today + timedelta(days=offset)
                DoctorAvailability.objects.get_or_create(
                    doctor=doctor,
                    date=avail_date,
                    start_time=time(9, 0),
                    end_time=time(13, 0),
                    defaults={"is_available": True}
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded hospital data!"))
