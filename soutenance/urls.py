from django.contrib import admin
from django.urls import path
from soutenance.views import views, admin  as soutenance_admin, auth, document, forlder, session, student, teacher, theme

urlpatterns = [
    #AUTHENTIFICATION
    path('login', auth.login_view, name='login'),
    path('login-post', auth.login_post, name='login-post'),
    path('logout', auth.logout_view, name='logout'),
    path('register', auth.register_view, name='register'),
    path('register_post', auth.register_post, name='register_post'),
    
    #DOCUMENT
    path('auto_save/<int:id>/', document.auto_save, name='auto_save'),
    path('create_document', document.create_document, name='create_document'),
    path('documents/<uuid:uid>/', document.view_document, name='view_document'),
    path('delete_document/<int:id>/', document.delete_document, name='delete_document'),
    path('rename_document/<int:id>/', document.rename_document, name='rename_document'),
    path('add_colaborateur_document/<int:id>/', document.add_colaborateur_document, name='add_colaborateur_document'),
    path('delete_colaborateur_document/<str:ids>/', document.delete_colaborateur_document, name='delete_colaborateur_document'),
    path('validate_shared_document/<int:user_id>-<int:document_id>/', document.validate_shared_document, name='validate_shared_document'),
    
    #FOLDER
    path('create_folder', forlder.create_folder, name='create_folder'),
    path('folders/<uuid:uid>/', forlder.view_folder, name='view_folder'),
    path('rename_folder/<int:id>/', forlder.rename_folder, name='rename_folder'),
    path('delete_folder/<int:id>/', forlder.delete_folder, name='delete_folder'),   
    path('add_colaborateur_folder/<int:id>/', forlder.add_colaborateur_folder, name='add_colaborateur_folder'),
    path('delete_colaborateur_folder/<str:ids>/', forlder.delete_colaborateur_folder, name='delete_colaborateur_folder'),
    path('validate_shared_folder/<int:user_id>-<int:folder_id>/', forlder.validate_shared_folder, name='validate_shared_folder'),
    
    #ADMIN
    path('session/<uuid:uid>/', soutenance_admin.admin_session, name='session'),
    path('level', soutenance_admin.admin_level, name='level'),
    path('sector', soutenance_admin.admin_sector, name='sector'),
    path('student', soutenance_admin.admin_student, name='student'),
    path('teacher', soutenance_admin.admin_teacher, name='teacher'),
    
    #SESSION
    path('create_session', session.create_session, name='create_session'),
    path('add_supervisor_session', session.add_supervisor_session, name='add_supervisor_session'),
    
    #TEACHER
    path('add_teacher', teacher.add_teacher, name='add_teacher'),
    
    #STUDENT
    path('add_student', student.add_student, name='add_student'),
    
    #THEME
    path('create_theme', theme.create_theme, name='create_theme'),
    path('student_validate_theme/<int:user_id>-<int:theme_id>/', theme.student_validate_theme, name='student_validate_theme'),
    
    #VIEWS
    path('', views.index, name='index'),
    path('notification', views.notification, name='notification'),
    path('home', views.home, name='home'),
    
]