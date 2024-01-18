from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from ckeditor.fields import RichTextField
from django.contrib.auth.models import BaseUserManager
import uuid

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, matricule, last_name, first_name, gender, date_of_birth, address, phone_number, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(
            matricule=matricule,
            last_name=last_name,
            first_name=first_name,
            gender=gender,
            date_of_birth=date_of_birth,
            address=address,
            phone_number=phone_number,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricule, last_name=None, first_name=None, gender=None, date_of_birth=None, address=None, phone_number=None, email=None, password=None, **extra_fields):
        # Ensure all required fields are passed to create_user
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            matricule=matricule,
            last_name=last_name,
            first_name=first_name,
            gender=gender,
            date_of_birth=date_of_birth,
            address=address,
            phone_number=phone_number,
            email=email,
            password=password
        )

class CustomUser(AbstractBaseUser, PermissionsMixin):
    matricule = models.CharField(max_length=20, unique=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'matricule'
    objects = CustomUserManager()  # Use your custom manager
    
class Folder(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='folder_created')
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    shared = models.ManyToManyField(CustomUser, through='FolderSharing', through_fields=('folder', 'user'))
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    timeLastUpdated = models.TimeField(auto_now=True)
    
class Document(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='documents_created')
    title = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = RichTextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=[('word', 'Word'), ('excel', 'Excel')], default='word')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    shared = models.ManyToManyField(CustomUser, through='DocumentSharing', through_fields=('document', 'user'))
    is_favorite = models.BooleanField(default=False)
    
class FolderSharing(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)

class DocumentSharing(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)

# Inutiles
# class Notification(models.Model):
#     id_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
#     id_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
#     id_enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
#     message = models.TextField()
#     date_heure = models.DateTimeField()
#     par_etudiant = models.CharField(max_length=3, choices=[('oui', 'Oui'), ('non', 'Non')])

# class StatutNotification(models.Model):
#     id_notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
#     id_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
#     status = models.CharField(max_length=255, choices=[('vue', 'Vue'), ('nonvue', 'Non vue')])

# class Role(models.Model):
#     ROLE_CHOICES = [
#         ('Encadreur', 'Encadreur'),
#         ('Superviseur', 'Superviseur'),
#     ]

#     type = models.CharField(max_length=20, choices=ROLE_CHOICES)

#     def __str__(self):
#         return self.type

# class RoleList(models.Model):
#     id_enseignant = models.ForeignKey('Enseignant', on_delete=models.CASCADE)
#     id_session = models.ForeignKey('Session', on_delete=models.CASCADE)
#     id_role = models.ForeignKey('Role', on_delete=models.CASCADE)

#     def __str__(self):
#         return f"Enseignant: {self.id_enseignant}, Session: {self.id_session}, Role: {self.id_role}"

# class DocumentGroupe(models.Model):
#     nom = models.CharField(max_length=255)
#     type = models.CharField(max_length=10, choices=[('word', 'Word'), ('excel', 'Excel')])
#     url = models.URLField()
#     id_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)

# class EtudiantGroupe(models.Model):
#     id_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
#     id_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
#     id_session = models.ForeignKey(Session, on_delete=models.CASCADE)

# class Planning(models.Model):
#     id_session = models.ForeignKey(Session, on_delete=models.CASCADE)
#     position = models.IntegerField()
#     tache = models.CharField(max_length=255)
#     erreur = models.CharField(max_length=255)
#     periode = models.CharField(max_length=255)
#     description = models.TextField()

# class Niveau(models.Model):
#     nom = models.CharField(max_length=255)

#     def __str__(self):
#         return self.nom
    
# class Admin(models.Model):
#     adresse_mail = models.EmailField(unique=True)
#     nom_utilisateur = models.CharField(max_length=255, unique=True)
#     mot_de_passe = models.CharField(max_length=255)
#     type = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('superadmin', 'SuperAdmin')])

# class Enseignant(models.Model):
   
#     type = models.CharField(max_length=10, choices=[('vacataire', 'Vacataire'), ('plein', 'Plein')])
#     user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)

#     email = models.EmailField()

# class Etudiant(models.Model):
#     user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
#     id_niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)

# class Session(models.Model):
#     nom = models.CharField(max_length=255)
#     annee = models.IntegerField()
#     niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
#     max_groupe = models.IntegerField()

# class Groupe(models.Model):
#     id_session = models.ForeignKey(Session, on_delete=models.CASCADE)
#     numero = models.IntegerField()
#     theme = models.CharField(max_length=255)

# class GroupeEnseignant(models.Model):
#     id_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
#     id_enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
