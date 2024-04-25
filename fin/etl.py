# etl.py

import csv
from fin.models import *
from datetime import datetime
from dateutil import parser
import pandas as pd

def convertir_nom_colonne(nom_colonne):
    if nom_colonne.lower() == 'tva':
        return 'TVA'
    elif nom_colonne.lower() == 'total ttc':
        return 'Total TTC'
    else:
        return nom_colonne.capitalize()

def determiner_categorie(row):
    if pd.isna(row['Nom du fournisseur']):
        return 'Vente'
    elif pd.isna(row['Nom du client']):
        return 'Achat'
    else:
        return None
    
# Fonction de transformation
def transform(data):
    df = pd.DataFrame(data)
    print(df)
    def convertir_date(date_str):
        try:
            date_obj = parser.parse(date_str)  # Analyse la date
            return date_obj.strftime('%d/%m/%Y')  # Convertit en format "jour/mois/année"
        except:
            return "Format de date invalide"

    df['date'] = df['date'].apply(convertir_date)
    print(df)
    df['tva'] = df['tva'].str.rstrip('%').astype(float) / 100
     # Utilisez replace sur l'ensemble du DataFrame en spécifiant regex=True
    df = df.replace(r'[;*+_\'"=)(|{}!?#[\]].', '', regex=True)
    df.columns = df.columns.map(convertir_nom_colonne)
    # Afficher les données avec les noms de colonnes convertis en majuscules
    df = df.sort_values(by='Date', ascending=True)
    print(df)
    df = df[[ 'Date', 'Numéro de facture', 'Nom du fournisseur','Nom du client' ,'Libellé', 'Prix unitaire', 'Quantité', 'TVA', 'Total hors taxe', 'Total TTC']]  
    df['Catégorie'] = df.apply(determiner_categorie, axis=1)
    print(df)
    return df

# Fonction de chargement
def load(data, dataimport_instance ):
   for index, row in data.iterrows():
        facture = Facture(fichier= dataimport_instance ,date=row['Date'], numero_facture=row['Numéro de facture'],
                           nom_fournisseur=row['Nom du fournisseur'], nom_client=row['Nom du client'],
                         libelle=row['Libellé'],prix_unitaire=row['Prix unitaire'],total_ttc=row['Total TTC'],
                         quantite=row['Quantité'],tva=row['TVA'],
                         total_hors_taxe=row['Total hors taxe'],catéogorie=row['Catégorie'])
        facture.save()
   print(data) 

# Appel des fonctions ETL

