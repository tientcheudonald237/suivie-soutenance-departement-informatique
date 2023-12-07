from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Enseignant)
admin.site.register(Etudiant)
admin.site.register(Niveau)
admin.site.register(Session)
admin.site.register(Document)
admin.site.register(CustomUser)


