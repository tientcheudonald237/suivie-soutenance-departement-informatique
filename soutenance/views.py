from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Document, CustomUser, DocumentSharing
from .forms import DocumentForm
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest

""" Page """

def index(request):
    if request.user.is_authenticated:
        user_documents = Document.objects.filter(user=request.user)
        shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)
        context = {
            'user_documents': user_documents,
            'shared_documents': shared_documents,
        }
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html')

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

def login_view(request):
    print(request.user.id)
    return render(request, 'authentification/login.html')

def login_post(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        password = request.POST.get('password')
        
        # Utilisez le champ correct pour l'authentification (par exemple, username ou email)
        user = authenticate(request, username=matricule, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        
    context = {
        'ERROR' : 'authentification',
        'ERROR_MESSAGE' : 'Invalide matricule ou mot de passe'
    }
    
    return render(request, 'authentification/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')  


""" Gestion Document """

def create_document(request):
    if request.method == 'POST':
        document_name = request.POST.get('document_name')
        document_type = request.POST.get('document_type')

        if request.user.is_authenticated:
            current_user = request.user    
            if document_type == 'word' :
                document = Document(title=document_name, content="", user=current_user, type=document_type) 
                document.save()
                messages.success(request, 'Document created successfully.')
                document_url = reverse('view_document', args=[document.id])
                return redirect(document_url)
            
        else : 
            messages.warning(request, 'Erreur Utilisateur non connecté') 
             
        
    return redirect('index')

def view_document(request,id):
    document = get_object_or_404(Document, id=id)  
    user_documents = Document.objects.filter(user=request.user)
    documentForm = DocumentForm(initial={'content': document.content})
    
    read_only_mode = request.GET.get('read-only', False) == 'true'
    
    domain = request.META['HTTP_HOST']
    domain_name = f'http://{domain}/view_document/{id}/?read-only=true'
    
    shared_documents = Document.objects.filter(documentsharing__user=request.user.id, documentsharing__accepted=True)
    active_tab = 'my_documents' if document in user_documents else 'shared_documents' if document in shared_documents else None


    if request.method == 'POST':
        edit_form = DocumentForm(request.POST, instance=document)
        if edit_form.is_valid():
            edit_form.save()     
            documentForm = DocumentForm(initial={'content': document.content}) 
    
    shared_users_not_accepted = CustomUser.objects.filter(documentsharing__document_id=id, documentsharing__accepted=False)
    shared_users_accepted = CustomUser.objects.filter(documentsharing__document_id=id, documentsharing__accepted=True)
    
    
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
        
def delete_document(request, id):
    try:
        document = Document.objects.get(id=id)
        document.delete()
        return HttpResponse(status=200)
    except Document.DoesNotExist:
        return JsonResponse({'message': 'Document not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)
    
def rename_document(request, id):
    document = get_object_or_404(Document, id=id)

    document_name = request.POST.get('document_name', '').strip()

    if not document_name:
        return HttpResponseBadRequest('Document name cannot be empty.')

    document.title = document_name
    document.save()
    
    return redirect('view_document', id=id)

def auto_save(request, id):
    document = get_object_or_404(Document, id=id)
    content = request.POST.get('content')
    print(content)
    document.content = str (content)
    document.save()

    return HttpResponse('Document saved successfully.', status=200)

    
""" ajout utilisateur dans un document  """

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
            
    return redirect('view_document', id=id)

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

def validate_shared_user(request, user_id, document_id):
    document_sharing = get_object_or_404(DocumentSharing, user_id=user_id, document_id=document_id)
    document_sharing.accepted = True
    document_sharing.save()
    return redirect('view_document', id=document_id)
    

""" Errors pages  """

def errors_404():
    pass