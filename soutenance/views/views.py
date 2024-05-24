import asyncio
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from ..models import Document, Folder, Student, StudentSession, Theme
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .admin import admin_index
from asgiref.sync import sync_to_async

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
    if request.user.is_authenticated:
        student_sessions = StudentSession.objects.filter(student=request.user)
        session_themes = []

      #  for student_session in student_sessions:
       #     session = student_session.session
        #    themes = Theme.objects.filter(session=session)
         #   has_theme = themes.filter(themestudent__student=request.user).exists()
        
        #for theme in themes :
        #    folder = Folder.objects.get(of_a_theme_id=theme.id)
         #   count_folder_sharing_from_student = folder.foldersharing_set.filter(is_from_student=True).count()
          #  if count_folder_sharing_from_student >= 1 :
           #     themes.remove(theme)

        for student_session in student_sessions:
            session = student_session.session
            themes = Theme.objects.filter(session=session)
            has_theme = themes.filter(themestudent__student=request.user).exists()

            themes_to_remove = []

            for theme in themes:
                folder = Folder.objects.get(of_a_theme_id=theme.id)
                count_folder_sharing_from_student = folder.foldersharing_set.filter(is_from_student=True).count()

                if count_folder_sharing_from_student >= 1:
                    themes_to_remove.append(theme)

            for theme_to_remove in themes_to_remove:
                themes = themes.exclude(id=theme_to_remove.id)

            session_themes.append({
                'session': session,
                'themes': themes,
                'has_theme': has_theme,
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



@csrf_exempt
def get_content(request,id):
    document = get_object_or_404(Document, id=id)
    content = document.content

    return JsonResponse({'content': content})

async def sse_updates(request, id):
    async def event_stream():
        document = await sync_to_async(get_object_or_404)(Document, id=id)  
        initial_content = document.content
        yield f"data: {initial_content}\n\n"

        while True:
            await asyncio.sleep(1)  
            document = await sync_to_async(Document.objects.get)(id=id) # type: ignore
            new_content = document.content
            #if new_content != initial_content:
            initial_content = new_content
            yield f"data: {initial_content}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response
