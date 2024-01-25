from django.shortcuts import render
from .models import  DocumentSharing, Folder, FolderSharing, Level, Sector
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


def get_parents_folder(folder):
    parent_folders = []
    current_folder = folder.parent_folder

    while current_folder is not None:
        parent_folders.insert(0, current_folder)  
        current_folder = current_folder.parent_folder

    return parent_folders

def get_parents_document(document):
    parent_folders = []
    current_folder = document.folder

    while current_folder is not None:
        parent_folders.insert(0, current_folder)  
        current_folder = current_folder.parent_folder

    return parent_folders

def has_access_to_folder(user, folder):
    if folder.user == user:
        return True

    if FolderSharing.objects.filter(user=user, folder=folder, accepted=True).exists():
        return True

    if folder.parent_folder:
        return has_access_to_folder(user, folder.parent_folder)

    return False

def has_access_to_document(user, document):
    if document.user == user:
        return True

    if DocumentSharing.objects.filter(user=user, document=document, accepted=True).exists():
        return True

    if document.folder:
        return has_access_to_folder(user, document.folder)

    return False


@csrf_exempt
def admin_index(request):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    context = {
        'levels': levels,
        'sectors': sectors,
    }
    return render(request, 'admin/session.html', context)

@csrf_exempt
def admin_sector(request):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    context = {
        'levels': levels,
        'sectors': sectors,
    }
    return render(request, 'admin/sector.html', context)

@csrf_exempt
def admin_level(request):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    context = {
        'levels': levels,
        'sectors': sectors,
    }
    return render(request, 'admin/level.html', context)