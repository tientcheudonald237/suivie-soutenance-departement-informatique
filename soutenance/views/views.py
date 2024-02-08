from django.shortcuts import render, redirect
from ..models import Document, Folder, Student, StudentSession, Theme
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .admin import admin_index

@csrf_exempt
@login_required(login_url='login')
def home(request):
    user = request.user
    
    if user.is_superuser:
        return admin_index(request)
    else:
        return redirect('index')

@csrf_exempt
@login_required(login_url='login')
def index(request):
    if request.user.is_authenticated :

        student_sessions = StudentSession.objects.filter(student=request.user)
        session_themes = []
        for student_session in student_sessions:
            session = student_session.session
            themes = Theme.objects.filter(session=session).exclude(themestudent__student=request.user)
            session_themes.append({
                'session': session,
                'themes': themes
            })

        user_folders = Folder.objects.filter(user=request.user, parent_folder=None)
        shared_folders = Folder.objects.filter(
        foldersharing__user=request.user.id,
            foldersharing__accepted=True,
        ).distinct()

        user_documents = Document.objects.filter(user=request.user, folder__isnull=True)
        shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)
                
        context = {
            'shared_folders': shared_folders,
            'user_folders': user_folders,
            'user_documents': user_documents,
            'shared_documents': shared_documents,
            'session_themes': session_themes, 
        }
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')

@csrf_exempt
@login_required(login_url='login')
def notification(request):
    if request.user.is_authenticated:
        user_folders = Folder.objects.filter(user=request.user, parent_folder=None)
        shared_folders = Folder.objects.filter(
        foldersharing__user=request.user.id,
            foldersharing__accepted=True,
        ).distinct()
        
        user_documents = Document.objects.filter(user=request.user, folder__isnull=True)
        shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True, folder__isnull=True)

        documents_not_accepted = Document.objects.filter(documentsharing__user_id=request.user.id, documentsharing__accepted=False)
        folders_not_accepted = Folder.objects.filter(foldersharing__user_id=request.user.id, foldersharing__accepted=False)
        context = {
            'shared_folders': shared_folders,
            'user_folders': user_folders,
            'user_documents': user_documents,
            'shared_documents': shared_documents,
            'documents_not_accepted': documents_not_accepted,
            'folders_not_accepted': folders_not_accepted,
        }
        return render(request, 'notification.html', context)
    else:
        return render(request, 'notification.html', context)

def errors_404():
    pass

