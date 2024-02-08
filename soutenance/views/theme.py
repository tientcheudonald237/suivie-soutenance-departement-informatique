from django.shortcuts import get_object_or_404, render, redirect
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

            folder = Folder(name=f"Groupe{numero}: {name}", user=request.user, of_a_theme=theme)
            parent_folder = Folder.objects.get(of_a_session=session)
            if parent_folder :
                folder.parent_folder = parent_folder
            folder.save()
            
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
    FolderSharing.objects.create(folder=theme_folder, user=student, accepted=True)
    messages.success(request, 'Le choix de votre theme est valider !!!')
    return index(request)       