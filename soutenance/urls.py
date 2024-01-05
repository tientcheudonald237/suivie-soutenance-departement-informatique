from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('notification', views.notification, name='notification'),
    path('login', views.login_view, name='login'),
    path('login-post', views.login_post, name='login-post'),
    path('create_document', views.create_document, name='create_document'),
    path('view_document/<int:id>/', views.view_document, name='view_document'),
    path('auto_save/<int:id>/', views.auto_save, name='auto_save'),
    path('delete_document/<int:id>/', views.delete_document, name='delete_document'),
    path('rename_document/<int:id>/', views.rename_document, name='rename_document'),
    path('add_colaborateur/<int:id>/', views.add_colaborateur, name='add_colaborateur'),
    path('delete_colaborateur/<str:ids>/', views.delete_colaborateur, name='delete_colaborateur'),
    path('validate_shared_user/<int:user_id>-<int:document_id>/', views.validate_shared_user, name='validate_shared_user'),
    path('logout', views.logout_view, name='logout'),
]