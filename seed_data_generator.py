import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_soutenaces.settings')
django.setup()

import random
from faker import Faker
from soutenance.models  import Level, Sector, Student, Teacher
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

fake = Faker()

User = get_user_model()

def seed_teachers(num_teachers=10):
    for _ in range(num_teachers):
        teacher = Teacher.objects.create(
            matricule=f'21Q{fake.unique.random_number(digits=4)}',
            last_name=fake.last_name(),
            first_name=fake.first_name(),
            gender=random.choice(['M', 'F']),
            date_of_birth=fake.date_of_birth(),
            address=fake.address(),
            phone_number=fake.phone_number(),
            email=fake.email(),
            is_staff=True,
            is_superuser=False,
            password = make_password("00000000"),
        )
        print(teacher.matricule)
        teacher.save()

def seed_students(num_students=20):
    levels = Level.objects.all()
    sectors = Sector.objects.all()

    for _ in range(num_students):
        student = Student.objects.create(
            matricule=f'21Q{fake.unique.random_number(digits=4)}',
            last_name=fake.last_name(),
            first_name=fake.first_name(),
            gender=random.choice(['M', 'F']),
            date_of_birth=fake.date_of_birth(),
            address=fake.address(),
            phone_number=fake.phone_number(),
            email=fake.email(),
            is_staff=False,
            is_superuser=False,
            password = make_password("00000000"),
            level = random.choice(levels),
            sector = random.choice(sectors)
        )
        print(student.matricule)
        student.save()

# seed_teachers()
seed_students()


