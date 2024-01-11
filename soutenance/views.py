from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Document, CustomUser, Folder, FolderSharing, DocumentSharing
from .forms import DocumentForm
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q

""" Page """

@csrf_exempt
def index(request):
    if request.user.is_authenticated:
        user_folders = Folder.objects.filter(user=request.user, parent_folder=None)
        shared_folders = Folder.objects.filter(
            foldersharing__user=request.user.id,
            foldersharing__accepted=True,
            parent_folder__foldersharing__user=request.user.id,
            parent_folder__foldersharing__accepted=True
        ).distinct()

        context = {
            'shared_folders': shared_folders,
            'user_folders': user_folders,
        }
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')

@csrf_exempt
def notification(request):
    context = {}
    
    if request.user.is_authenticated:
        user_documents = Document.objects.filter(user=request.user)
        
        documents_not_accepted = Document.objects.filter(documentsharing__user_id=request.user.id, documentsharing__accepted=False)

        context = {
            'user_documents': user_documents,
            'documents_not_accepted': documents_not_accepted,
        }
    
    return render(request, 'notification.html', context)

""" Connexion """

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
        
    context = {
        'ERROR' : 'authentification',
        'ERROR_MESSAGE' : 'Invalide matricule ou mot de passe'
    }
    
    return render(request, 'authentification/login.html', context)

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
                document.folder = request.POST.get('parent_folder')
            document.save()
            messages.success(request, 'Document created successfully.')
            document_url = reverse('view_document', args=[document.id])
            return redirect(document_url)
            
        else : 
            messages.warning(request, 'Erreur Utilisateur non connecté') 
             
        
    return redirect('index')

@csrf_exempt
def view_document(request,uid):
    document = get_object_or_404(Document, uid=uid)  
    user_documents = Document.objects.filter(user=request.user)
    documentForm = DocumentForm(initial={'content': document.content})
    
    read_only_mode = request.GET.get('read-only', False) == 'true'
    
    domain = request.META['HTTP_HOST']
    domain_name = f'http://{domain}/view_document/{uid}/?read-only=true'
    
    shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)
    active_tab = 'my_documents' if document in user_documents else 'shared_documents' if document in shared_documents else None


    if request.method == 'POST':
        edit_form = DocumentForm(request.POST, instance=document)
        if edit_form.is_valid():
            edit_form.save()     
            documentForm = DocumentForm(initial={'content': document.content}) 
    
    shared_users_not_accepted = CustomUser.objects.filter(documentsharing__document_id=document.id, documentsharing__accepted=False)
    shared_users_accepted = CustomUser.objects.filter(documentsharing__document_id=document.id, documentsharing__accepted=True)
    
    
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
    
    return redirect('view_document', id=id)

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
def add_colaborateur(request, id):
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
def delete_colaborateur(request, ids):
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
def validate_shared_user(request, user_id, document_id):
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
        folder.save()
        
        messages.success(request, 'Folder created successfully.')
        return redirect('index')
       
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

    return redirect('index')

def view_folder(request, uid):
    folder = get_object_or_404(Folder, uid=uid)
    subfolders = Folder.objects.filter(parent_folder=folder)
    documents = Document.objects.filter(folder=folder)

    user_folders = Folder.objects.filter(user=request.user, parent_folder=None)
    shared_folders = Folder.objects.filter(
        foldersharing__user=request.user.id,
        foldersharing__accepted=True,
        parent_folder__foldersharing__user=request.user.id,
        parent_folder__foldersharing__accepted=True
    ).distinct()
    
    context ={
        "folder" : folder,
        "subfolders": subfolders,
        "documents": documents,
        'shared_folders': shared_folders,
        'user_folders': user_folders,
    }
    
    return render(request, 'view_folder.html', context)
    