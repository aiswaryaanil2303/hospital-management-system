import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from hospital.models import Category, Doctor, Patient, DoctorAvailability, Appointment, Prescription


class Command(BaseCommand):
    help = "Safely restores the original hospital data from original_hospital_backup.json if modified/dummy data is detected."

    def handle(self, *args, **options):
        has_dummy_doctors = Doctor.objects.filter(
            email__in=["dr.aiswarya@hospital.com", "dr.smith@hospital.com"]
        ).exists()

        if not has_dummy_doctors and Doctor.objects.filter(email="solly123@gmail.com").exists():
            self.stdout.write(self.style.SUCCESS("Original doctor data is already active and intact. No changes needed."))
            return

        self.stdout.write("Modified doctor data detected on Render. Restoring original doctor data...")

        self.stdout.write("Step 1: Creating backup of current database state...")
        backup_file = "pre_restore_backup.json"
        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                call_command("dumpdata", "hospital", indent=4, stdout=f)
            self.stdout.write(self.style.SUCCESS(f"Pre-restore backup saved to {backup_file}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not dump current data: {e}"))

        self.stdout.write("Step 2: Cleaning up dummy records introduced by previous changes...")
        Doctor.objects.filter(email__in=["dr.aiswarya@hospital.com", "dr.smith@hospital.com"]).delete()
        Category.objects.filter(name__in=["Neurology", "Orthopedics", "General Medicine"]).delete()

        self.stdout.write("Step 3: Loading original authentic data from original_hospital_backup.json...")
        fixture_path = "original_hospital_backup.json"
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f"Fixture file not found: {fixture_path}"))
            return

        call_command("loaddata", fixture_path)

        self.stdout.write(self.style.SUCCESS("\nSuccessfully restored original hospital data!\n"))

        self.stdout.write("--- RESTORED DOCTORS ---")
        for doc in Doctor.objects.all().order_by("id"):
            self.stdout.write(f"ID {doc.id}: {doc.name} | {doc.email} | {doc.phone} | Category: {doc.category.name} | Photo: {doc.photo.name or 'None'}")

        self.stdout.write("\n--- RESTORED PATIENTS ---")
        for pat in Patient.objects.all().order_by("id"):
            self.stdout.write(f"ID {pat.id}: {pat.name} | {pat.email} | {pat.phone}")

        self.stdout.write("\n--- RESTORED CATEGORIES ---")
        for cat in Category.objects.all().order_by("id"):
            self.stdout.write(f"ID {cat.id}: {cat.name}")
