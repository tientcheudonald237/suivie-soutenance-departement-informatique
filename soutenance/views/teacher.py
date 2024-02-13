from datetime import datetime
from django.forms import ValidationError
from django.shortcuts import  get_object_or_404, redirect
import pandas as pd
from ..models import Teacher
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view
from django.core.serializers import serialize
from ..serializers import TeacherSerializer
from django.http import JsonResponse
from rest_framework.response import Response

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


def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.delete()
    return JsonResponse({'message': 'Teacher deleted successfully'}, status=200)


def update_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        teacher.last_name = request.POST.get('last_name')
        teacher.first_name = request.POST.get('first_name')
        teacher.email = request.POST.get('email')
        teacher.gender = request.POST.get('gender')
        teacher.date_of_birth = request.POST.get('date_of_birth')
        teacher.address = request.POST.get('address')
        teacher.phone_number = request.POST.get('phone_number')
        teacher.save()
        messages.success(request, 'Informations de l\'enseignant modifier avec succes.')
    return redirect('teacher')


@api_view(['GET'])
def get_teacher(request, teacher_id):
    try:
        teacher = get_object_or_404(Teacher, id=teacher_id)
        serializer = TeacherSerializer(teacher)
        return Response(serializer.data)
    except Teacher.DoesNotExist:
        return JsonResponse({'data': 'off'}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({'data': 'off'}, status=500)


def upload_teachers(request):
    if request.method == 'POST':
        file = request.FILES.get('fileInput')

        # Vérifier si un fichier a été sélectionné
        if not file:
            messages.error(request, "Veuillez sélectionner un fichier Excel.")
            return redirect('teacher')

        # Traiter le fichier téléchargé
        error_message = process_uploaded_file(file)

        if error_message:
            messages.error(request, error_message)
        else:
            messages.success(request, "Enregistrment reussi, toute informations mal emise n'as pas été prise en compte.")
            return redirect('teacher')

    return redirect('teacher')


def process_uploaded_file(file):
    try:
        # Charger le fichier Excel en un DataFrame pandas
        df = pd.read_excel(file)

        # Valider que toutes les colonnes nécessaires sont présentes
        required_columns = ['matricule', 'last_name', 'first_name', 'gender', 'date_of_birth', 'address', 'phone_number', 'email']
        for column in required_columns:
            if column not in df.columns:
                raise ValidationError(f'La colonne {column} est manquante dans le fichier Excel.')
            
        # Parcourir chaque ligne du DataFrame et créer un objet teacher pour chaque ligne
        for index, row in df.iterrows():
            print(f"Matricule: {row['matricule']}")
            print(f"Last Name: {row['last_name']}")
            print(f"First Name: {row['first_name']}")
            print(f"Gender: {row['gender']}")
            print(f"Date of Birth: {row['date_of_birth']}")
            print(f"Address: {row['address']}")
            print(f"Phone Number: {row['phone_number']}")
            print(f"Email: {row['email']}")
            existing_teacher = Teacher.objects.filter(matricule=row['matricule']).first()
    
            if existing_teacher:
                # Si un enseignant avec le même matricule existe déjà, passez à la ligne suivante
                print("existe deja")
                continue


            gender = row['gender']
            if gender not in ['M', 'F']:
                print("probleme de genre")
                continue

            date_format = '%Y-%m-%d %H:%M:%S'  # Format pour 'AAAA-MM-JJ HH:MM:SS'
            date_of_birth = str(row['date_of_birth'])
            try:
                datetime.strptime(date_of_birth, date_format)
            except Exception as e:
                print(e)
                continue

            hashed_password = make_password("00000000")
            Teacher.objects.create(
                matricule=row['matricule'],
                last_name=row['last_name'],
                first_name=row['first_name'],
                gender=row['gender'],
                date_of_birth=row['date_of_birth'],
                address=row['address'],
                phone_number=row['phone_number'],
                email=row['email'],
                password=hashed_password,
            )
            print("Enregistrer")

    except Exception as e:
        # Gérer les erreurs lors du traitement du fichier
        return str("verifier vos champs, une erreur est survenu !!")
        return str(e)

    return None