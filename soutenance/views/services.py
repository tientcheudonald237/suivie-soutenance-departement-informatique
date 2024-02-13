from django.shortcuts import render, redirect
from ..models import  Document, DocumentSharing, Folder, FolderSharing, Level, Sector, Teacher, Session, TeacherTheme, Theme, Student
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password

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


def delete_folder_and_children(folder_id):
    # Récupérer le dossier et ses enfants récursivement
    folder = Folder.objects.get(id=folder_id)
    child_folders = Folder.objects.filter(parent_folder=folder)
    documents = Document.objects.filter(folder=folder)

    # Supprimer les documents du dossier et les relations de partage
    for document in documents:
        document_sharing = DocumentSharing.objects.filter(document=document)
        document_sharing.delete()

    documents.delete()

    # Supprimer les relations de partage pour le dossier
    folder_sharing = FolderSharing.objects.filter(folder=folder)
    folder_sharing.delete()

    # Récursivement supprimer les sous-dossiers
    for child_folder in child_folders:
        delete_folder_and_children(child_folder.id)

    # Enfin, supprimer le dossier lui-même
    folder.delete()