from django.db import models



# User models
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
    matricule = models.CharField(max_length=20, unique=True)
    mot_de_passe = models.CharField(max_length=255)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    sexe = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    date_de_naissance = models.DateField()
    type = models.CharField(max_length=10, choices=[('vacataire', 'Vacataire'), ('plein', 'Plein')])
    adresse = models.TextField()
    numero_telephone = models.CharField(max_length=20)
    email = models.EmailField()

class Etudiant(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    mot_de_passe = models.CharField(max_length=255)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    sexe = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    date_de_naissance = models.DateField()
    adresse = models.TextField()
    numero_telephone = models.CharField(max_length=20)
    email = models.EmailField()
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

class DocumentEnseignant(models.Model):
    nom = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=[('word', 'Word'), ('excel', 'Excel')])
    url = models.URLField()
    id_enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    visibilite = models.CharField(max_length=20, choices=[('tous_le_monde', 'Tous le monde'),
                                                          ('enseignants_session', 'Enseignants de la session'),
                                                          ('seul', 'Seul')])

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


#Hello 