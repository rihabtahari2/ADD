from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import matplotlib.pyplot as plt
from fin.models import *
from django.db.models import Sum, Case, When, IntegerField
from django.db.models.functions import ExtractMonth

# Récupérer les données de vente par mois pour les achats
import matplotlib.pyplot as plt

# Exemple de données
categories = ['Achat', 'Vente']
valeurs = [10, 20]

# Créer le diagramme en secteurs
plt.figure(figsize=(8, 8))
plt.pie(valeurs, labels=categories, autopct='%1.1f%%', startangle=140)
plt.axis('equal')  # Assure que le diagramme est un cercle
plt.title('Répartition des catégories')
plt.show()