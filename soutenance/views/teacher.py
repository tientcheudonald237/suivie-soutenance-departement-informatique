from django.shortcuts import  redirect
from ..models import Teacher
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password

@csrf_exempt
@login_required(login_url='login')
def add_teacher(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')

        if matricule and last_name and first_name and gender and date_of_birth and address and phone_number and email  :
            hashed_password = make_password("00000000")
            
            teacher = Teacher(
                matricule=matricule,
                last_name=last_name,
                first_name=first_name,
                gender=gender,
                date_of_birth=date_of_birth,
                address=address,
                phone_number=phone_number,
                email=email,
                password=hashed_password,
            )

            teacher.save()
            messages.success(request, 'Nouveau enseignant enregistrer.')
        else:    
            messages.error(request, 'Toute les informations doivent etre saisi.')
        return redirect('teacher')  

    return redirect('teacher')  
