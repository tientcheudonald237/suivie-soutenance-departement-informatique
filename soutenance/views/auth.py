from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from ..models import  Admin
from django.urls import reverse
from django.http import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

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
        return redirect('home') 
    
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
            return redirect('home')
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
