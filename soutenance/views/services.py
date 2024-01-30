from django.shortcuts import render, redirect
from ..models import  DocumentSharing, Folder, FolderSharing, Level, Sector, Teacher, Session, TeacherTheme, Theme, Student
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
