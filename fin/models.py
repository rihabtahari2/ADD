from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User 
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class ExpertProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.user) +'_ExpertProfile_'

class AssistantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expert_profile = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return str(self.user) + '_AssistantProfile_'

class Données(models.Model):
    Nom = models.CharField(max_length=100)
    date = models.DateField(unique=True)
    Valuer = models.CharField(max_length=100)  
    def __str__(self):
        return self.Nom

def validate_caracteres(value):
    caracteres_permitidos = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    caracteres_invalides = set(value) - set(caracteres_permitidos)
    if caracteres_invalides:
        raise ValidationError(f"Les caractères suivants ne sont pas autorisés dans le nom du client : {' '.join(caracteres_invalides)}")
    
class client(models.Model):
    clientId=models.AutoField(primary_key=True)
    clientName=models.CharField(max_length=500,validators=[validate_caracteres])
    clientAdresse=models.CharField(max_length=500,default=' ')
    clientActivity=models.CharField(max_length=500, default=' ')
    contact = models.EmailField(max_length=254,default='example@example.com')
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Expertprofile=models.ForeignKey(ExpertProfile,on_delete=models.CASCADE, null=True)
    def __str__(self): 
        return self.clientName
# Create your models here.

class UserClient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(client, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'client')

class Person(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    city = models.CharField(max_length=100)
    new_column = models.CharField(max_length=100, null=True, blank=True)
    date = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class dataimport(models.Model):
    Id=models.AutoField(primary_key=True)
    nom= models.CharField(max_length=100,default=" ")
    description= models.CharField(max_length=700,default=" ")
    client = models.ForeignKey(client, on_delete=models.CASCADE,default=0 )
    Expertprofile=models.ForeignKey(ExpertProfile,on_delete=models.CASCADE, null=True)
    Assistantprofile=models.ForeignKey(AssistantProfile,on_delete=models.CASCADE, null=True)
    def __str__(self): 
        return self.nom    

from datetime import datetime     
class Facture(models.Model):
    id = models.AutoField(primary_key=True)
    Date = models.DateTimeField(default=datetime(2022, 1, 1, 0, 0, 0))
    date=models.CharField(max_length=50,default=" ")
    fichier = models.ForeignKey(dataimport, on_delete=models.CASCADE,default="")
    numero_facture = models.CharField(max_length=100)
    nom_fournisseur = models.CharField(max_length=255)
    nom_client = models.CharField(max_length=255,default=" ")
    libelle = models.CharField(max_length=255)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.IntegerField()
    tva = models.DecimalField(max_digits=5, decimal_places=2)
    total_hors_taxe = models.DecimalField(max_digits=10, decimal_places=2)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    catéogorie = models.CharField(max_length=70,default=' ')
    

    def __str__(self):
        return self.libelle
class Dim_client_ent(models.Model):
    Id=models.AutoField(primary_key=True)
    nom=models.CharField(max_length=500,validators=[validate_caracteres])
    Adresse=models.CharField(max_length=500,default=' ')
    Activity=models.CharField(max_length=500, default=' ')
    email = models.EmailField(max_length=254,default='example@example.com')
    def __str__(self):
        return self.nom

class Dim_Produit(models.Model):
    id_produit = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=100)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.libelle
    
class Dim_Temps(models.Model):
    id_temps = models.AutoField(primary_key=True)
    id_Tempss=models.CharField(max_length=500)
    jour=models.CharField(max_length=2)
    mois = models.CharField(max_length=2)
    annee = models.IntegerField()
    def __str__(self):
        return self. id_Tempss
    
class Dim_Client(models.Model):
    id_client = models.AutoField(primary_key=True)
    nom_client = models.CharField(max_length=100)
    def __str__(self):
        return self.nom_client
class fait_vente(models.Model):
    id_ligne_facture = models.AutoField(primary_key=True)
    id_client = models.ForeignKey(Dim_Client, on_delete=models.CASCADE)
    id_produit = models.ForeignKey(Dim_Produit, on_delete=models.CASCADE)
    id_temps = models.ForeignKey(Dim_Temps, on_delete=models.CASCADE)
    client_ent= models.ForeignKey(Dim_client_ent, on_delete=models.CASCADE,default="")
    TVA = models.DecimalField(max_digits=10, decimal_places=2)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    total_hors_taxe = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.IntegerField()
    CA = models.DecimalField(max_digits=10, decimal_places=2,default=Decimal('0.00'))
    def __str__(self):
        return str(self.total_ttc)
    
class Dim_Fournisseur(models.Model):
    id_fournisseur = models.AutoField(primary_key=True)
    nom_fournisseur = models.CharField(max_length=100)
    def __str__(self):
        return self.nom_fournisseur
    
class fait_achat(models.Model):
    id_ligne_facture = models.AutoField(primary_key=True)
    id_produit = models.ForeignKey(Dim_Produit, on_delete=models.CASCADE)
    id_fournisseur = models.ForeignKey(Dim_Fournisseur, on_delete=models.CASCADE)
    id_temps = models.ForeignKey(Dim_Temps, on_delete=models.CASCADE)
    client_ent= models.ForeignKey(Dim_client_ent, on_delete=models.CASCADE,default="")
    TVA = models.DecimalField(max_digits=10, decimal_places=2)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    total_hors_taxe = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.IntegerField()
    def __str__(self):
        return str(self.total_ttc)