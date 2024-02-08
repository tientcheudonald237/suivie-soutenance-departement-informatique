from django.shortcuts import redirect
from django.contrib import messages
from ..models import Folder, Level, Sector, Session, Student, StudentSession, Teacher
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
