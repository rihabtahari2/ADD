from django.db import models
from django.contrib.auth.models import User 
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


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

