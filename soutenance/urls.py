from django.contrib import admin
from django.urls import path
from .import views
from soutenance import services

urlpatterns = [
    path('', views.index, name='index'),
    path('notification', views.notification, name='notification'),
    path('login', views.login_view, name='login'),
    path('login-post', views.login_post, name='login-post'),
    path('auto_save/<int:id>/', views.auto_save, name='auto_save'),
    path('create_document', views.create_document, name='create_document'),
    path('documents/<uuid:uid>/', views.view_document, name='view_document'),
    path('delete_document/<int:id>/', views.delete_document, name='delete_document'),
    path('rename_document/<int:id>/', views.rename_document, name='rename_document'),
    path('logout', views.logout_view, name='logout'),
    path('create_folder', views.create_folder, name='create_folder'),
    path('folders/<uuid:uid>/', views.view_folder, name='view_folder'),
    path('rename_folder/<int:id>/', views.rename_folder, name='rename_folder'),
    path('delete_folder/<int:id>/', views.delete_folder, name='delete_folder'),   
    path('add_colaborateur_document/<int:id>/', views.add_colaborateur_document, name='add_colaborateur_document'),
    path('delete_colaborateur_document/<str:ids>/', views.delete_colaborateur_document, name='delete_colaborateur_document'),
    path('validate_shared_document/<int:user_id>-<int:document_id>/', views.validate_shared_document, name='validate_shared_document'),
    path('add_colaborateur_folder/<int:id>/', views.add_colaborateur_folder, name='add_colaborateur_folder'),
    path('delete_colaborateur_folder/<str:ids>/', views.delete_colaborateur_folder, name='delete_colaborateur_folder'),
    path('validate_shared_folder/<int:user_id>-<int:folder_id>/', views.validate_shared_folder, name='validate_shared_folder'),
    path('supervisor', services.admin_supervisor, name='supervisor'),
    #session
    path('create_session', views.create_session, name='create_session'),
    path('level', services.admin_level, name='level'),
    path('sector', services.admin_sector, name='sector'),
]