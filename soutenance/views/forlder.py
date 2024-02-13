from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Document, CustomUser, Folder
from django.urls import reverse
from django.http import  JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from itertools import groupby
from operator import attrgetter
from .services import *


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
        #folder = Folder.objects.get(id=id)
        delete_folder_and_children(id)
        #folder.delete()
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

@csrf_exempt
@login_required(login_url='login')
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
    user_folders_ = Folder.objects.filter(user=request.user)
    shared_folders = Folder.objects.filter(
        foldersharing__user=request.user.id,
        foldersharing__accepted=True,
    ).distinct()
    
    
    user_documents = Document.objects.filter(user=request.user, folder__isnull=True)
    shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)
    active_tab = 'my_folder' if folder in user_folders else 'shared_folder' if folder in shared_folders else None
    active_action = 'my_folder' if folder in user_folders_ else 'shared_folder' if folder in shared_folders else None
    parent_folders = get_parents_folder(folder)
    
    shared_users_not_accepted = CustomUser.objects.filter(foldersharing__folder_id=folder.id, foldersharing__accepted=False)
    shared_users_accepted = CustomUser.objects.filter(foldersharing__folder_id=folder.id, foldersharing__accepted=True)
    
    if request.user.is_superuser :
        active_tab = 'my_document'
        active_action = 'my_folder'
        
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
        'active_action': active_action,
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
