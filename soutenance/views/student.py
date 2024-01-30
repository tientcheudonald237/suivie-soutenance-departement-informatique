from django.shortcuts import redirect
from ..models import  Student
from django.contrib import messages
from django.contrib.auth.hashers import make_password


def add_student(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        sector_id = request.POST.get('sector_id')
        level_id = request.POST.get('level_id')
        hashed_password = make_password("00000000")
        try:
            student = Student.objects.create(
                matricule=matricule,
                last_name=last_name,
                first_name=first_name,
                email=email,
                gender=gender,
                date_of_birth=date_of_birth,
                address=address,
                phone_number=phone_number,
                sector_id=sector_id,
                level_id=level_id,
                password=hashed_password
            )
            messages.success(request, 'Student created successfully.')
        except Exception as e:
            messages.error(request, f'Error creating student: {e}')

    return redirect('student')