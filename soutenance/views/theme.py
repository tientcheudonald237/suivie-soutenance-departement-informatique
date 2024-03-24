from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view 
from soutenance.serializers import ThemeSerializer
from soutenance.views.services import delete_folder_and_children
from ..models import Folder, FolderSharing, Student, Teacher, Session, TeacherTheme, Theme, ThemeStudent
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .views import index

@csrf_exempt
def create_theme(request):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        name = request.POST.get('name')
        description = request.POST.get('description')
        session_id = request.POST.get('id_session')
        
        session = Session.objects.get(id=session_id)
        
        try:
            theme = Theme.objects.create(
                numero=numero,
                name=name,
                description=description,
                session=session
            )
                
            teachers_ids = request.POST.getlist('teachers')  

            for teacher_id in teachers_ids:
                teacher = Teacher.objects.get(id=teacher_id)
                TeacherTheme.objects.create(theme=theme, teacher=teacher)

            folder = Folder(name=name, user=request.user, of_a_theme=theme)
            parent_folder = Folder.objects.get(of_a_session=session)
            if parent_folder :
                folder.parent_folder = parent_folder
            folder.save()
            
            # Partager le dossier du thème avec tous les enseignants associés
            for teacher_id in teachers_ids:
                teacher = Teacher.objects.get(id=teacher_id)
                FolderSharing.objects.create(folder=folder, user=teacher, accepted=True, is_from_student=False)
            
            messages.success(request, 'Theme enregistrer.')
            

        except Exception as e:
            messages.error(request, f"Une erreur s'est produite : {str(e)}")
        
    return redirect('session', uid=session.uid)

@csrf_exempt
def student_validate_theme(request, user_id, theme_id):
    student = get_object_or_404(Student, id=user_id)
    theme = get_object_or_404(Theme, id=theme_id)
    
    ThemeStudent.objects.create(student=student, theme=theme)
    theme_folder = Folder.objects.get(of_a_theme=theme)
    FolderSharing.objects.create(folder=theme_folder, user=student, accepted=True, is_from_student=True)
    messages.success(request, 'Le choix de votre theme est valider !!!')
    return redirect('index')      

@csrf_exempt
def delete_theme(request, theme_id):
    try:
        theme = get_object_or_404(Theme, id=theme_id)
    
        folder = Folder.objects.get(of_a_theme=theme)
        delete_folder_and_children(folder.id)

        # Supprimer les relations TeacherTheme
        TeacherTheme.objects.filter(theme=theme).delete()

        # Supprimer les relations ThemeStudent
        ThemeStudent.objects.filter(theme=theme).delete()
        
        # Supprimer le thème lui-même
        theme.delete()    
        return JsonResponse({'message': 'Thème supprimé avec succès'}, status=200)
    except Theme.DoesNotExist:
        return JsonResponse({'error': 'Le thème spécifié n\'existe pas'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f"Une erreur s'est produite : {str(e)}"}, status=500)
    
@api_view(['GET'])
def get_theme(request, theme_id):
    try:
        theme = get_object_or_404(Theme, id=theme_id)
        serializer = ThemeSerializer(theme)
        return Response(serializer.data)
    except Theme.DoesNotExist:
        return JsonResponse({'data': 'off'}, status=404)
    except Exception as e:
        return JsonResponse({'data': 'off'}, status=500)


@csrf_exempt
def update_theme(request, theme_id):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        name = request.POST.get('name')
        description = request.POST.get('description')
        session_id = request.POST.get('id_session')

        session = Session.objects.get(id=session_id)
        
        try:
            theme = Theme.objects.get(id=theme_id)
            theme.numero = numero
            theme.name = name
            theme.description = description
            theme.session = session  # Mettre à jour la session du thème
            theme.save()

            # Supprimer d'abord tous les enseignants associés au thème
            theme.teachers.clear()

            teachers_ids = request.POST.getlist('teachers')  

            for teacher_id in teachers_ids:
                teacher = Teacher.objects.get(id=teacher_id)
                theme.teachers.add(teacher)

            # Supprimer tous les partages de dossier précédents pour les enseignants associés au thème
            folder = Folder.objects.get(of_a_theme=theme)
            FolderSharing.objects.filter(folder=folder, accepted=True, is_from_student=False).delete()

            # Partager à nouveau le dossier du thème avec les enseignants mis à jour
            for teacher_id in teachers_ids:
                teacher = Teacher.objects.get(id=teacher_id)
                FolderSharing.objects.create(folder=folder, user=teacher, accepted=True, is_from_student=False)

            messages.success(request, 'Thème mis à jour avec succès.')
            
        except Theme.DoesNotExist:
            messages.error(request, 'Le thème spécifié n\'existe pas.')
        except Session.DoesNotExist:
            messages.error(request, 'La session spécifiée n\'existe pas.')
        except Teacher.DoesNotExist:
            messages.error(request, 'L\'enseignant spécifié n\'existe pas.')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite lors de la mise à jour du thème : {str(e)}")
        
    return redirect('session', uid=session.uid)