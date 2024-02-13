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
            session.supervisor.add(*teachers)

            return redirect('session', uid=session.uid)

        except Session.DoesNotExist:
            messages.error(request, 'La session spécifiée n\'existe pas.')
        except Teacher.DoesNotExist:
            messages.error(request, 'Un enseignant spécifié n\'existe pas.')

    return redirect('session')

def delete_session(request, uid):
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