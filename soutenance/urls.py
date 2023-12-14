from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('login-post', views.login_post, name='login-post'),
    path('create_document/', views.create_document, name='create_document'),
    path('view_document/<int:id>/', views.view_document, name='view_document'),
    path('delete_document/<int:id>/', views.delete_document, name='delete_document'),

]