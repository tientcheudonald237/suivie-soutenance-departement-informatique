from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from ckeditor.fields import RichTextField




# User models

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    use_in_migrations=True
    def _create_user(self, matricule, nom, prenom, sexe, date_de_naissance, adresse, numero_telephone, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(
            matricule=matricule,
            nom=nom,
            prenom=prenom,
            sexe=sexe,
            date_de_naissance=date_de_naissance,
            adresse=adresse,
            numero_telephone=numero_telephone,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    """def create_user(self, email, name, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, name, phone, password, **extra_fields)"""
    def create_superuser(self, matricule, nom=None, prenom=None, sexe=None, date_de_naissance=None, adresse=None, numero_telephone=None, email=None, password=None, **extra_fields):
        # Ensure all required fields are passed to create_user
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            matricule=matricule,
            nom=nom,
            prenom=prenom,
            sexe=sexe,
            date_de_naissance=date_de_naissance,
            adresse=adresse,
            numero_telephone=numero_telephone,
            email=email,
            password=password
        )


class CustomUser(AbstractBaseUser,PermissionsMixin):

    matricule = models.CharField(max_length=20, unique=True)
    #mot_de_passe = models.CharField(max_length=255)
    nom = models.CharField(max_length=255,blank=True,null=True)
    prenom = models.CharField(max_length=255,blank=True,null=True)
    sexe = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')],blank=True,null=True)
    date_de_naissance = models.DateField(blank=True,null=True)
    adresse = models.TextField(blank=True,null=True)
    numero_telephone = models.CharField(max_length=20,blank=True,null=True)
    email = models.EmailField(blank=True,null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD='matricule'
    #REQUIRED_FIELDS=['nom','prenom','sexe']
    objects = CustomUserManager()  # Use your custom manager

    
    
class Niveau(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom
class Admin(models.Model):
    adresse_mail = models.EmailField(unique=True)
    nom_utilisateur = models.CharField(max_length=255, unique=True)
    mot_de_passe = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('superadmin', 'SuperAdmin')])

class Enseignant(models.Model):
   
    type = models.CharField(max_length=10, choices=[('vacataire', 'Vacataire'), ('plein', 'Plein')])
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)

    email = models.EmailField()

class Etudiant(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    id_niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)

class Session(models.Model):
    nom = models.CharField(max_length=255)
    annee = models.IntegerField()
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    max_groupe = models.IntegerField()



class Groupe(models.Model):
    id_session = models.ForeignKey(Session, on_delete=models.CASCADE)
    numero = models.IntegerField()
    theme = models.CharField(max_length=255)

class GroupeEnseignant(models.Model):
    id_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    id_enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)

class Document(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    datePosted = models.CharField(max_length=20, default="")
    timePosted = models.CharField(max_length=20, default="")
    category = models.CharField(max_length=300, default="rha")
    content = RichTextField(blank=True, null=True)
    """id_enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    visibilite = models.CharField(max_length=20, choices=[('tous_le_monde', 'Tous le monde'),
                                                          ('enseignants_session', 'Enseignants de la session'),
                                                          ('seul', 'Seul')])"""

class DocumentGroupe(models.Model):
    nom = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=[('word', 'Word'), ('excel', 'Excel')])
    url = models.URLField()
    id_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)

class EtudiantGroupe(models.Model):
    id_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    id_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    id_session = models.ForeignKey(Session, on_delete=models.CASCADE)

class Planning(models.Model):
    id_session = models.ForeignKey(Session, on_delete=models.CASCADE)
    position = models.IntegerField()
    tache = models.CharField(max_length=255)
    periode = models.CharField(max_length=255)
    description = models.TextField()

# Notification models
class Notification(models.Model):
    id_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    id_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    id_enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    message = models.TextField()
    date_heure = models.DateTimeField()
    par_etudiant = models.CharField(max_length=3, choices=[('oui', 'Oui'), ('non', 'Non')])

class StatutNotification(models.Model):
    id_notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    id_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=[('vue', 'Vue'), ('nonvue', 'Non vue')])


class Role(models.Model):
    ROLE_CHOICES = [
        ('Encadreur', 'Encadreur'),
        ('Superviseur', 'Superviseur'),
    ]

    type = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.type

class RoleList(models.Model):
    id_enseignant = models.ForeignKey('Enseignant', on_delete=models.CASCADE)
    id_session = models.ForeignKey('Session', on_delete=models.CASCADE)
    id_role = models.ForeignKey('Role', on_delete=models.CASCADE)

    def __str__(self):
        return f"Enseignant: {self.id_enseignant}, Session: {self.id_session}, Role: {self.id_role}"
