from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Document

def index(request):
    if request.user.is_authenticated:
        user_documents = Document.objects.filter(user=request.user)
        context = {'user_documents': user_documents}
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')
    
def login(request):
    return render(request, 'authentification/login.html')

def login_post(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        password = request.POST.get('password')
        
        user = authenticate(request, matricule=matricule, password=password)

        if user is not None:
            login(request)
            return redirect('index') 
        
    context = {
        'ERROR' : 'authentification',
        'ERROR_MESSAGE' : 'Invalide matricule ou mot de passe'
    }
    
    return render(request,'authentification/login.html', context)

def create_document(request):
    if request.method == 'POST':
        document_name = request.POST.get('document_name')

        if request.user.is_authenticated:
            current_user = request.user    
            document = Document(title=document_name, user=current_user,category="exemple") 
            document.save()
            messages.success(request, 'Document created successfully.')
        else : 
            messages.warning(request, 'Erreur Utilisateur n\'ont connecter') 
        
        return redirect('index')

    return render(request, 'index.html')

def view_document(request,id):
    # document = get_object_or_404(Document, id=id)
    document = Document()
    user_documents = Document.objects.filter(user=request.user)
    context = {
        'document': document,
        'user_documents': user_documents,
    }
    return render(request, 'view_document.html', context)