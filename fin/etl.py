# etl.py

import csv
from fin.models import *
from datetime import datetime
from dateutil import parser
import pandas as pd

from pymongo import MongoClient
# Connexion à la base de données MongoDB
client = MongoClient('localhost', 27017)
# Utilisation de la base de données
db = client['rihab']

def convertir_nom_colonne(nom_colonne):
    if nom_colonne.lower() == 'tva':
        return 'TVA'
    elif nom_colonne.lower() == 'total ttc':
        return 'Total TTC'
    else:
        return nom_colonne.capitalize()

def determiner_categorie(row):
    if pd.isna(row['Nom du fournisseur']):  # Si le nom du fournisseur est manquant
        return 'Vente'  # Alors c'est une vente
    elif pd.isna(row['Nom du client']):  # Sinon, si le nom du client est manquant
        return 'Achat'  # Alors c'est un achat
    else:
        return None  # Sinon, aucun des deux
# Fonction de transformation
def transform(data):
    df = pd.DataFrame(data)
    def convertir_date(date_str):
        try:
            date_obj = pd.to_datetime(date_str, dayfirst=True)  # Analyse de la date en spécifiant que le jour est en premier
            return date_obj.strftime('%d/%m/%Y')  # Convertit en format "jour/mois/année"
        except:
            return "Format de date invalide"
    df['date'] = df['date'].apply(convertir_date)
    print(df)
    df['tva'] = df['tva'].str.rstrip('%').astype(float) / 100
     # Utilisez replace sur l'ensemble du DataFrame en spécifiant regex=True
    df = df.replace(r'[;*+_\'"=)(|{}!?#[\]].', '', regex=True)
    df['time'] = pd.to_datetime(df['time'])
    # Fusionner les colonnes 'Date' et 'Heure' en une seule colonne 'Date'
    df['Date1'] = df['date']+ ' ' + df['time'].dt.strftime('%H:%M:%S')
    df.columns = df.columns.map(convertir_nom_colonne)# Afficher les données avec les noms de colonnes convertis en majuscules
    #trier les date par ordre croissante
    def custom_sort(date_str):
        return int(date_str.split('/')[1]) 
    df_sorted = df.sort_values(by='Date1', key=lambda x: x.map(custom_sort))
    df =df_sorted[['Date1', 'Numéro de facture', 'Nom du fournisseur','Nom du client' ,'Libellé', 'Prix unitaire', 
             'Quantité', 'TVA', 'Total hors taxe', 'Total TTC']]  
    df['Catégorie'] = df.apply(determiner_categorie, axis=1)
    print(df)
    return df

# Fonction de chargement
def load(data, dataimport_instance,dim_client_ent):
    for index, row in data.iterrows():
        produit, _ = Dim_Produit.objects.get_or_create(
            libelle=row['Libellé'],
            defaults={'prix_unitaire': row['Prix unitaire']}
        )
        num_fac, _ =Dim_facture.objects.get_or_create(
            num_fac=row['Numéro de facture']
        )
        # Remplir Dim_Temps
        date_facture = datetime.strptime(row['Date1'], '%d/%m/%Y %H:%M:%S')
        # Créer une instance de DimTemps
        temps, _ = Dim_Temps.objects.get_or_create(
            id_Tempss=date_facture,
            jour=date_facture.day,
            mois=date_facture.month,
            annee=date_facture.year
        )
        # Remplir Dim_Client
        if pd.notna(row['Nom du client']):
            # Créer une instance de DimClient
            client, _ = Dim_Client.objects.get_or_create(
                nom_client=row['Nom du client']
            )
            ca = row['Prix unitaire'] * row['Quantité']
            # les jointure
            # Créer une instance de fait_vente en utilisant les instances récupérées
            nouvelle_vente = fait_vente.objects.create(
                id_client=client,
                id_produit=produit,
                id_temps=temps,
                client_ent=dim_client_ent,
                TVA=row['TVA'],
                total_ttc=row['Total TTC'],
                total_hors_taxe=row['Total hors taxe'],
                quantite=row['Quantité'],
                CA=ca,
                id_fact=num_fac,
                id_user=dataimport_instance,
            )

        # Remplir Dim_Fournisseur
        if pd.notna(row['Nom du fournisseur']):
            # Créer une instance de DimFournisseur
            fournisseur, _ = Dim_Fournisseur.objects.get_or_create(
                nom_fournisseur=row['Nom du fournisseur']
            )
             # Créer une instance de fait_vente en utilisant les instances récupérées
            nouvelle_achat = fait_achat.objects.create(
                id_fournisseur=fournisseur,
                id_produit=produit,
                id_temps=temps,
                client_ent=dim_client_ent,
                TVA=row['TVA'],
                total_ttc=row['Total TTC'],
                total_hors_taxe=row['Total hors taxe'],
                quantite=row['Quantité'],
                id_fact=num_fac,
                id_user=dataimport_instance,
            )








        facture = Facture(fichier= dataimport_instance ,date=row['Date1'], numero_facture=row['Numéro de facture'],
                           nom_fournisseur=row['Nom du fournisseur'], nom_client=row['Nom du client'],
                         libelle=row['Libellé'],prix_unitaire=row['Prix unitaire'],total_ttc=row['Total TTC'],
                         quantite=row['Quantité'],tva=row['TVA'],
                         total_hors_taxe=row['Total hors taxe'],catéogorie=row['Catégorie'])
        facture.save()
 

# Fermeture de la connexion
client.close()


