from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from soutenance.views.services import delete_folder_and_children
from ..models import Document, DocumentSharing, Folder, FolderSharing, Level, Sector, Session, Student, StudentSession, Teacher, TeacherTheme, Theme, ThemeStudent
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def create_session(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        year = request.POST.get('year')
        level_id = request.POST.get('level_id')
        sector_id = request.POST.get('sector_id')
        max_groupe = request.POST.get('max_groupe')
        print(f'{name} {year} {level_id} {sector_id} {max_groupe}')
        if name and year and sector_id and  level_id and max_groupe:
            level = Level.objects.get(pk=level_id)
            sector = Sector.objects.get(pk=sector_id)
            session = Session.objects.create(
                name=name,
                year=year,
                level=level,
                sector=sector,
                max_groupe=max_groupe
            )
            
            folder = Folder(name=name, user=request.user)
            folder.of_a_session = session
            folder.save()
            
            students_same_level_sector = Student.objects.filter(level=level, sector=sector)

            for student in students_same_level_sector:
                StudentSession.objects.create(student=student, session=session)
        
            messages.success(request, 'Session creer avec success.')
            return redirect('home') 
        else:
            messages.error(request, 'Tous les champs sont necessaires')
            return redirect(request.session.get('previous_url', reverse('home')))
    
    return redirect('home')

def add_supervisor_session(request):
    if request.method == 'POST':
        teacher_ids = request.POST.getlist('teachers')
        session_id = request.POST.get('id_session')

        try:
            session = Session.objects.get(id=session_id)
            teachers = Teacher.objects.filter(id__in=teacher_ids)
            
            # Ajoute les enseignants comme superviseurs de la session
            session.supervisor.add(*teachers)
            
            # Récupère le dossier propre à la session
            session_folder = Folder.objects.get(of_a_session=session)
            
            # Ajoute les enseignants comme collaborateurs du dossier de la session
            for teacher in teachers:
                FolderSharing.objects.get_or_create(folder=session_folder, user=teacher, accepted=True, is_from_student=False)
            
            return redirect('session', uid=session.uid)

        except Session.DoesNotExist:
            messages.error(request, 'La session spécifiée n\'existe pas.')
        except Teacher.DoesNotExist:
            messages.error(request, 'Un enseignant spécifié n\'existe pas.')

    return redirect('session')


def delete_supervisor_session(request, session_id, teacher_id):
    try:
        session = Session.objects.get(id=session_id)
        teacher = Teacher.objects.get(id=teacher_id)
        
        # Supprimer l'enseignant du partage de dossier
        session_folder = Folder.objects.get(of_a_session=session)
        FolderSharing.objects.filter(folder=session_folder, user=teacher).delete()
        
        # Supprimer l'enseignant de la liste des superviseurs de la session
        session.supervisor.remove(teacher)
        
        messages.success(request, f"L'enseignant {teacher} a été retiré en tant que superviseur de la session {session.name} et du partage de dossier.")
    except Session.DoesNotExist:
        messages.error(request, 'La session spécifiée n\'existe pas.')
    except Teacher.DoesNotExist:
        messages.error(request, 'L\'enseignant spécifié n\'existe pas.')

    return redirect('session', uid=session.uid)


def delete_session(request):
    session = get_object_or_404(Session, uid=uid)

    # Supprimer les dossiers liés aux thèmes
    for theme in Theme.objects.filter(session=session):
        folder = Folder.objects.get(of_a_theme=theme)
        delete_folder_and_children(folder.id)

        # Supprimer les relations TeacherTheme
        TeacherTheme.objects.filter(theme=theme).delete()

        # Supprimer les relations ThemeStudent
        ThemeStudent.objects.filter(theme=theme).delete()
        
    # Supprimer les thèmes
    Theme.objects.filter(session=session).delete()

    # Supprimer les sessions d'étudiants liées
    StudentSession.objects.filter(session=session).delete()

    # Enfin, supprimer la session
    session.delete()

    return JsonResponse({'message': 'Session deleted successfully'}, status=200)

def add_student_session(request):
    if request.method == 'POST':
        students_ids = request.POST.getlist('students')
        session_id = request.POST.get('id_session')

        try:
            session = Session.objects.get(id=session_id)
            
            # Créer une session pour chaque étudiant sélectionné
            for student_id in students_ids:
                student = Student.objects.get(id=student_id)
                StudentSession.objects.create(student=student, session=session)

            messages.success(request, 'Étudiants ajoutés à la session avec succès.')
        except Session.DoesNotExist:
            messages.error(request, 'La session spécifiée n\'existe pas.')
        except Student.DoesNotExist:
            messages.error(request, 'Un étudiant spécifié n\'existe pas.')

    return redirect('session', uid=session.uid)

def delete_student_session(request, session_id, student_id):
    try:
        session = Session.objects.get(id=session_id)
        student = Student.objects.get(id=student_id)
        
        # Supprimer l'étudiant de la session
        StudentSession.objects.filter(session=session, student=student).delete()
        
        # Séparer l'étudiant de son thème associé
        ThemeStudent.objects.filter(theme__session=session, student=student).delete()
        
        # Séparer l'étudiant du dossier auquel il avait accès par rapport à la session
        try:
            student_folder = Folder.objects.get(user=student, of_a_session=session)            
            # Supprimer les partages de dossier pour l'étudiant
            FolderSharing.objects.filter(folder=student_folder, user=student).delete()
        except Folder.DoesNotExist:
            pass
        
        messages.success(request, f"L'étudiant {student} a été retiré de la session {session.name} et séparé de son thème et du dossier.")
    except Session.DoesNotExist:
        messages.error(request, 'La session spécifiée n\'existe pas.')
    except Student.DoesNotExist:
        messages.error(request, 'L\'étudiant spécifié n\'existe pas.')

    return redirect('session', uid=session.uid)
