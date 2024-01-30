from django.shortcuts import render, redirect
from ..models import  Level, Sector, StudentSession, Teacher, Session, Theme, Student
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password


@csrf_exempt
@login_required(login_url='login')
def admin_index(request):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    sessions = Session.objects.all()
    context = {
        'levels': levels,
        'sectors': sectors,
        'sessions': sessions,
    }
    return render(request, 'admin/home.html', context)

@csrf_exempt
@login_required(login_url='login')
def admin_sector(request):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    sessions = Session.objects.all()
    context = {
        'levels': levels,
        'sectors': sectors,
        'sessions': sessions,
    }
    return render(request, 'admin/sector.html', context)

@csrf_exempt
@login_required(login_url='login')
def admin_student(request):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    sessions = Session.objects.all()
    students = Student.objects.all()
    context = {
        'levels': levels,
        'sectors': sectors,
        'sessions': sessions,
        'students': students,
    }
    return render(request, 'admin/student.html', context)


@csrf_exempt
@login_required(login_url='login')
def admin_level(request):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    sessions = Session.objects.all()
    context = {
        'levels': levels,
        'sectors': sectors,
        'sessions': sessions,
    }
    return render(request, 'admin/level.html', context)

@csrf_exempt
@login_required(login_url='login')
def admin_teacher(request):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    teachers = Teacher.objects.all()
    sessions = Session.objects.all()
    context = {
        'levels': levels,
        'sectors': sectors,
        'teachers': teachers,
        'sessions': sessions,
    }
    return render(request, 'admin/teacher.html', context)


@csrf_exempt
@login_required(login_url='login')
def admin_session(request, uid):
    levels = Level.objects.all()
    sectors = Sector.objects.all()
    teachers = Teacher.objects.all()
    sessions = Session.objects.all()
    session = Session.objects.get(uid=uid)
    students_in_session = Student.objects.filter(studentsession__session=session)
    
    students_same_level_sector = Student.objects.filter(
        level=session.level,
        sector=session.sector
    ).exclude(id__in=students_in_session)
    
    themes = Theme.objects.filter(session=session).order_by('numero')
    supervisors = session.supervisor.all()
    no_supervisors = Teacher.objects.exclude(sessions_supervised__pk=session.pk)


    
    context = {
        'levels': levels,
        'sectors': sectors,
        'teachers': teachers,
        'sessions': sessions,
        'session': session,
        'themes': themes,
        'supervisors': supervisors,
        'no_supervisors': no_supervisors,
        'students_in_session': students_in_session,
        'students_same_level_sector': students_same_level_sector,
    }
    
    return render(request, 'admin/session.html', context)
