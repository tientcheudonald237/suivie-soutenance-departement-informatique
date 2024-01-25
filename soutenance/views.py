from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Document, CustomUser, Folder, FolderSharing, DocumentSharing, Teacher, Student, Admin, Level, Sector, Session
from .forms import DocumentForm
from django.urls import reverse
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from itertools import groupby
from operator import attrgetter
from .services import *

""" Page """

@csrf_exempt
def index(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        user = request.user
        
        if user.is_superuser:
            return admin_index(request)
        else:
            # return redirect('register')

            
            user_folders = Folder.objects.filter(user=request.user, parent_folder=None)
            shared_folders = Folder.objects.filter(
                foldersharing__user=request.user.id,
                foldersharing__accepted=True,
                parent_folder__foldersharing__user=request.user.id,
                parent_folder__foldersharing__accepted=True
            ).distinct()
            
            user_documents = Document.objects.filter(user=request.user, folder__isnull=True)
            shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)
            

            context = {
                'shared_folders': shared_folders,
                'user_folders': user_folders,
                'user_documents': user_documents,
                'shared_documents': shared_documents,
            }
            return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')

@csrf_exempt
def notification(request):
    if request.user.is_authenticated:
        user_folders = Folder.objects.filter(user=request.user, parent_folder=None)
        shared_folders = Folder.objects.filter(
            foldersharing__user=request.user.id,
            foldersharing__accepted=True,
            parent_folder__foldersharing__user=request.user.id,
            parent_folder__foldersharing__accepted=True
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

""" Connexion """

@csrf_exempt
def register_view(request):
    return render(request, 'authentification/register.html')

@csrf_exempt
def register_post(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        matricule = request.POST.get('matricule')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password-confirm')

        if password != password_confirm:
            messages.error(request, 'Password confirmation does not match.')
            return redirect('register')  

        admin_user = Admin.objects.create_superuser(
            matricule=matricule,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        login(request, admin_user)
        messages.success(request, 'Registration successful.')
        return redirect('index') 
    
@csrf_exempt
def login_view(request):
    return render(request, 'authentification/login.html')

@csrf_exempt
def login_post(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        password = request.POST.get('password')
        
        user = authenticate(request, username=matricule, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            context = {
                'ERROR': 'authentification',
                'ERROR_MESSAGE': 'Invalide matricule ou mot de passe'
            }
            return render(request, 'authentification/login.html', context)
    
    return HttpResponseNotAllowed(['POST'])
@csrf_exempt
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')  


""" Document """
@csrf_exempt
@login_required(login_url='login')
def create_document(request):
    if request.method == 'POST':
        document_name = request.POST.get('document_name')
        document_type = request.POST.get('document_type')

        current_user = request.user    
        if document_type == 'word' :
            document = Document(title=document_name, content="", user=current_user, type=document_type)
            
            if request.POST.get('parent_folder') :
                id_folder = int(request.POST.get('parent_folder'))
                parent_folder = get_object_or_404(Folder, pk=id_folder)
                document.folder = parent_folder
                
            document.save()
            messages.success(request, 'Document created successfully.')
            document_url = reverse('view_document', args=[document.uid])
            return redirect(document_url)
            
        else : 
            messages.warning(request, 'Erreur Utilisateur non connecté') 
             
    return redirect('index')

@csrf_exempt
def view_document(request,uid):
    document = get_object_or_404(Document, uid=uid)  
    

    # Vérifier si l'utilisateur a accès au document
    if not has_access_to_document(request.user, document):
        return render(request, 'errors/404.html')

    
    
    user_documents = Document.objects.filter(user=request.user, folder__isnull=True)
    documentForm = DocumentForm(initial={'content': document.content})
 
    read_only_mode = request.GET.get('read-only', False) == 'true'
    
    domain = request.META['HTTP_HOST']
    domain_name = f'http://{domain}/documents/{uid}/?read-only=true'
    
    shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)


    user_documents_ = Document.objects.filter(user=request.user)
    shared_documents_ = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)    
    active_tab = 'my_document' if document in user_documents_ else 'shared_document' if document in shared_documents_ else None

    if request.method == 'POST':
        edit_form = DocumentForm(request.POST, instance=document)
        if edit_form.is_valid():
            edit_form.save()     
            documentForm = DocumentForm(initial={'content': document.content}) 
    
    shared_users_not_accepted = CustomUser.objects.filter(documentsharing__document_id=document.id, documentsharing__accepted=False)
    shared_users_accepted = CustomUser.objects.filter(documentsharing__document_id=document.id, documentsharing__accepted=True)
    user_folders = Folder.objects.filter(user=request.user, parent_folder=None)
    shared_folders = Folder.objects.filter(
        foldersharing__user=request.user.id,
        foldersharing__accepted=True,
    ).distinct()
    parent_folders = get_parents_document(document)
    
    context = {
        'document': document,
        'user_documents': user_documents,
        'documentForm': documentForm,
        'read_only_mode': read_only_mode,
        'domaine_name' : domain_name,
        'shared_users_not_accepted' : shared_users_not_accepted,
        'shared_users_accepted' : shared_users_accepted,
        'shared_documents' : shared_documents,
        'active_tab': active_tab,
        'user_folders': user_folders,
        'shared_folders': shared_folders,
        'parent_folders': parent_folders,
    }
    return render(request, 'view_document.html', context)

@csrf_exempt 
@login_required(login_url='login')  
def delete_document(request, id):
    try:
        document = Document.objects.get(id=id)
        document.delete()
        return HttpResponse(status=200)
    except Document.DoesNotExist:
        return JsonResponse({'message': 'Document not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)
    
@csrf_exempt
@login_required(login_url='login')
def rename_document(request, id):
    document = get_object_or_404(Document, id=id)

    document_name = request.POST.get('document_name', '').strip()

    if not document_name:
        return HttpResponseBadRequest('Document name cannot be empty.')

    document.title = document_name
    document.save()
    
    return redirect('view_document', uid=document.uid)

@csrf_exempt
@login_required(login_url='login')
def auto_save(request, id):
    document = get_object_or_404(Document, id=id)
    content = request.POST.get('content')
    # print(f"-------{content}")
    document.content = str (content)
    document.save()

    return HttpResponse('Document saved successfully.', status=200)

    
""" ajout utilisateur dans un document  """
@csrf_exempt
@login_required(login_url='login')
def add_colaborateur_document(request, id):
    document = get_object_or_404(Document, id=id)
    
    if request.method == 'POST':
        matricule = request.POST.get('matricule')

        collaborateur = CustomUser.objects.filter(matricule=matricule).first()
        if collaborateur.id != document.user_id :
            if collaborateur:
                if collaborateur not in document.shared.all():
                    document.shared.add(collaborateur)
                    messages.success(request, f'{collaborateur.matricule} ajouté avec succès à la liste des collaborateurs.')
                else:
                    messages.warning(request, f'{collaborateur.matricule} est déjà dans la liste des collaborateurs.')
            else:
                messages.error(request, f'Aucun utilisateur trouvé avec le matricule {matricule}.')
        else:
            messages.warning(request, f'Vous ne pouvez pas vous ajouter au document')
            
    return redirect('view_document', uid=document.uid)

@csrf_exempt
@login_required(login_url='login')
def delete_colaborateur_document(request, ids):
    try:
        user_id, document_id = ids.split('-')
        user_id = int(user_id)
        document_id = int(document_id)
        document = get_object_or_404(Document, id=document_id)

        document.shared.remove(user_id)
    
        return HttpResponse(status=200)
    
    except Document.DoesNotExist:
        return JsonResponse({'message': 'Document not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

@csrf_exempt
@login_required(login_url='login')
def validate_shared_document(request, user_id, document_id):
    document = get_object_or_404(Document, id=document_id)
    document_sharing = get_object_or_404(DocumentSharing, user_id=user_id, document_id=document_id)
    document_sharing.accepted = True
    document_sharing.save()
    return redirect('view_document', uid=document.uid)

""" Errors pages  """

def errors_404():
    pass

""" Folder CRUD"""

@csrf_exempt
@login_required(login_url='login')
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        current_user = request.user
        
        folder = Folder(name=folder_name, user=current_user)
        if request.POST.get('parent_folder') :
            id_folder = int(request.POST.get('parent_folder'))
            parent_folder = get_object_or_404(Folder, pk=id_folder)
            folder.parent_folder = parent_folder
        folder.save()
        
        messages.success(request, 'Folder created successfully.')

        folder_url = reverse('view_folder', args=[folder.uid])
        return redirect(folder_url)
        
       
    return redirect('index')

@csrf_exempt
@login_required(login_url='login')
def delete_folder(request, id):
    try:
        folder = Folder.objects.get(id=id)
        folder.delete()
        return HttpResponse(status=200)
    except Folder.DoesNotExist:
        return JsonResponse({'message': 'Folder not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

@csrf_exempt
@login_required(login_url='login')
def rename_folder(request, id):
    folder = get_object_or_404(Folder, id=id)

    folder_name = request.POST.get('folder_name', '').strip()

    if not folder_name:
        return HttpResponseBadRequest('Folder name cannot be empty.')

    folder.name = folder_name
    folder.save()
    return redirect('view_folder', uid=folder.uid)


def view_folder(request, uid):
    folder = get_object_or_404(Folder, uid=uid)
    if not has_access_to_folder(request.user, folder):
        return render(request, 'errors/404.html')
    
    subfolders = Folder.objects.filter(parent_folder=folder).order_by('-created_at')
    documents = Document.objects.filter(folder=folder).order_by('-created_at')

        
    # Combine subfolders and documents into a single list
    all_items = list(subfolders) + list(documents)
    # Sort the combined list by created_at
    sorted_items = sorted(all_items, key=attrgetter('created_at'), reverse=True)
    # Group the sorted list by created_at
    grouped_items = {key: list(group) for key, group in groupby(sorted_items, key=lambda x: x.created_at.date())}
    

    user_folders = Folder.objects.filter(user=request.user, parent_folder=None)
    shared_folders = Folder.objects.filter(
        foldersharing__user=request.user.id,
        foldersharing__accepted=True,
    ).distinct()
    
    
    user_documents = Document.objects.filter(user=request.user, folder__isnull=True)
    shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)
    active_tab = 'my_folder' if folder in user_folders else 'shared_folder' if folder in shared_folders else None
    parent_folders = get_parents_folder(folder)
    
    shared_users_not_accepted = CustomUser.objects.filter(foldersharing__folder_id=folder.id, foldersharing__accepted=False)
    shared_users_accepted = CustomUser.objects.filter(foldersharing__folder_id=folder.id, foldersharing__accepted=True)
    
    context ={
        "folder" : folder,
        "grouped_items": grouped_items,
        'shared_folders': shared_folders,
        'user_folders': user_folders,
        'user_documents': user_documents,
        'shared_documents': shared_documents,
        'active_tab': active_tab,
        'parent_folders': parent_folders,
        'shared_users_not_accepted': shared_users_not_accepted,
        'shared_users_accepted': shared_users_accepted,
    }
    
    return render(request, 'view_folder.html', context)


@csrf_exempt
def add_colaborateur_folder(request, id):
    folder = get_object_or_404(Folder, id=id)
    
    if request.method == 'POST':
        matricule = request.POST.get('matricule')

        collaborateur = CustomUser.objects.filter(matricule=matricule).first()
        if collaborateur.id != folder.user_id :
            if collaborateur:
                if collaborateur not in folder.shared.all():
                    folder.shared.add(collaborateur)
                    messages.success(request, f'{collaborateur.matricule} ajouté avec succès à la liste des collaborateurs.')
                else:
                    messages.warning(request, f'{collaborateur.matricule} est déjà dans la liste des collaborateurs.')
            else:
                messages.error(request, f'Aucun utilisateur trouvé avec le matricule {matricule}.')
        else:
            messages.warning(request, f'Vous ne pouvez pas vous ajouter au document')
            
    return redirect('view_folder', uid=folder.uid)

@csrf_exempt
def delete_colaborateur_folder(request, ids):
    try:
        user_id, folder_id = ids.split('-')
        user_id = int(user_id)
        folder_id = int(folder_id)
        folder = get_object_or_404(Folder, id=folder_id)

        folder.shared.remove(user_id)
    
        return HttpResponse(status=200)
    
    except Document.DoesNotExist:
        return JsonResponse({'message': 'Document not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

@csrf_exempt
def validate_shared_folder(request, user_id, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    folder_sharing = get_object_or_404(FolderSharing, user_id=user_id, folder_id=folder_id)
    folder_sharing.accepted = True
    folder_sharing.save()
    return redirect('view_folder', uid=folder.uid)



""" SESSION CRUD"""

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
            Session.objects.create(
                name=name,
                year=year,
                level=level,
                sector=sector,
                max_groupe=max_groupe
            )
            messages.success(request, 'Session creer avec success.')
            return redirect('index') 
        else:
            messages.error(request, 'Tous les champs sont necessaires')
            return redirect(request.session.get('previous_url', reverse('index')))
    
    return redirect('index')