from django.http import JsonResponse
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from ..models import  Student, Level,  Sector
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view
from django.core.serializers import serialize
from ..serializers import StudentSerializer
import pandas as pd
from django.core.exceptions import ValidationError
from datetime import datetime

def add_student(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        
        existing_student = Student.objects.filter(matricule=matricule).first()
        if existing_student:
            messages.error(request, 'Un compte avec ce matricule existe deja')
            return redirect('student')
        
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

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return JsonResponse({'message': 'Student deleted successfully'}, status=200)


def update_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.last_name = request.POST.get('last_name')
        student.first_name = request.POST.get('first_name')
        student.email = request.POST.get('email')
        student.gender = request.POST.get('gender')
        student.date_of_birth = request.POST.get('date_of_birth')
        student.address = request.POST.get('address')
        student.phone_number = request.POST.get('phone_number')
        student.save()
        messages.success(request, 'Informations de l\'etudiant modifier avec succes.')
    return redirect('student')


@api_view(['GET'])
def get_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        serializer = StudentSerializer(student)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return JsonResponse({'data': 'off'}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({'data': 'off'}, status=500)


def upload_students(request):
    if request.method == 'POST':
        file = request.FILES.get('fileInput')

        # Vérifier si un fichier a été sélectionné
        if not file:
            messages.error(request, "Veuillez sélectionner un fichier Excel.")
            return redirect('student')

        # Traiter le fichier téléchargé
        error_message = process_uploaded_file(file)

        if error_message:
            messages.error(request, error_message)
        else:
            messages.success(request, "Enregistrment reussi, toute informations mal emise n'as pas été prise en compte.")
            return redirect('student')

    return redirect('student')


def process_uploaded_file(file):
    try:
        # Charger le fichier Excel en un DataFrame pandas
        df = pd.read_excel(file)

        # Valider que toutes les colonnes nécessaires sont présentes
        required_columns = ['matricule', 'last_name', 'first_name', 'gender', 'date_of_birth', 'address', 'phone_number', 'email', 'level', 'sector']
        for column in required_columns:
            if column not in df.columns:
                raise ValidationError(f'La colonne {column} est manquante dans le fichier Excel.')
            
        # Parcourir chaque ligne du DataFrame et créer un objet Student pour chaque ligne
        for index, row in df.iterrows():
            existing_student = Student.objects.filter(matricule=row['matricule']).first()
    
            if existing_student:
                # Si un étudiant avec le même matricule existe déjà, passez à la ligne suivante
                continue

            # Vérifier si le niveau existe, sinon lever une exception
            try:
                level_obj = Level.objects.get(name=row['level'])
            except Level.DoesNotExist:
                # Gérer le cas où le niveau n'existe pas
                # Vous pouvez ignorer cette ligne ou prendre une action spécifique
                continue

            # Vérifier si le secteur existe, sinon lever une exception
            try:
                sector_obj = Sector.objects.get(name=row['sector'])
            except Sector.DoesNotExist:
                # Gérer le cas où le secteur n'existe pas
                # Vous pouvez ignorer cette ligne ou prendre une action spécifique
                continue
            

            gender = row['gender']
            if gender not in ['M', 'F']:
                continue

            date_format = '%Y-%m-%d %H:%M:%S'  # Format pour 'AAAA-MM-JJ HH:MM:SS'
            date_of_birth = str(row['date_of_birth'])
            try:
                datetime.strptime(date_of_birth, date_format)
            except Exception as e:
                print(e)
                continue
            
            hashed_password = make_password("00000000")
            Student.objects.create(
                matricule=row['matricule'],
                last_name=row['last_name'],
                first_name=row['first_name'],
                gender=row['gender'],
                date_of_birth=row['date_of_birth'],
                address=row['address'],
                phone_number=row['phone_number'],
                email=row['email'],
                level=level_obj,
                sector=sector_obj,
                password=hashed_password,
            )

    except Exception as e:
        # Gérer les erreurs lors du traitement du fichier
        return str("verifier vos champs, une erreur est survenu !!")
        return str(e)

    return None
