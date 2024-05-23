# etl.py
from decimal import Decimal, InvalidOperation
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
def load(data, dataimport_instance):
    for index, row in data.iterrows():

        facture = Facture(fichier= dataimport_instance ,date=row['Date1'], numero_facture=row['Numéro de facture'],
                           nom_fournisseur=row['Nom du fournisseur'], nom_client=row['Nom du client'],
                         libelle=row['Libellé'],prix_unitaire=row['Prix unitaire'],total_ttc=row['Total TTC'],
                         quantite=row['Quantité'],tva=row['TVA'],
                         total_hors_taxe=row['Total hors taxe'],catéogorie=row['Catégorie'])
        facture.save()

def load_from_facture(dataimport_instance, dim_client_ent):
    factures = Facture.objects.filter(fichier=dataimport_instance)

    for facture in factures:
        try:
            # Convertir les valeurs Decimal128 en chaînes, puis en Decimal
            prix_unitaire = Decimal(str(facture.prix_unitaire))
            quantite = Decimal(str(facture.quantite))
            tva = Decimal(str(facture.tva))
            total_ttc = Decimal(str(facture.total_ttc))
            total_hors_taxe = Decimal(str(facture.total_hors_taxe))
        except InvalidOperation:
            # Si une des valeurs ne peut pas être convertie en Decimal, continuez à la facture suivante
            continue

        # Remplir Dim_Produit
        produit, _ = Dim_Produit.objects.get_or_create(
            libelle=facture.libelle,
            defaults={'prix_unitaire': prix_unitaire}
        )

        # Remplir Dim_facture
        num_fac, _ = Dim_facture.objects.get_or_create(
            num_fac=facture.numero_facture
        )

        # Remplir Dim_Temps
        date_facture = datetime.strptime(facture.date, '%d/%m/%Y %H:%M:%S')
        temps, _ = Dim_Temps.objects.get_or_create(
            id_Tempss=str(date_facture),
            defaults={
                'jour': str(date_facture.day),
                'mois': str(date_facture.month),
                'annee': date_facture.year
            }
        )

        # Remplir Dim_Client
        if facture.nom_client:
            client, _ = Dim_Client.objects.get_or_create(
                nom_client=facture.nom_client
            )

            # Calcul du chiffre d'affaires
            ca = prix_unitaire * quantite

            # Créer une instance de fait_vente
            fait_vente.objects.create(
                id_client=client,
                id_produit=produit,
                id_temps=temps,
                client_ent=dim_client_ent,
                TVA=tva,
                total_ttc=total_ttc,
                total_hors_taxe=total_hors_taxe,
                quantite=facture.quantite,
                CA=ca,
                id_fact=num_fac,
                id_user=dataimport_instance,
            )

        # Remplir Dim_Fournisseur
        if facture.nom_fournisseur:
            fournisseur, _ = Dim_Fournisseur.objects.get_or_create(
                nom_fournisseur=facture.nom_fournisseur
            )

            # Créer une instance de fait_achat
            fait_achat.objects.create(
                id_fournisseur=fournisseur,
                id_produit=produit,
                id_temps=temps,
                client_ent=dim_client_ent,
                TVA=tva,
                total_ttc=total_ttc,
                total_hors_taxe=total_hors_taxe,
                quantite=facture.quantite,
                id_fact=num_fac,
                id_user=dataimport_instance,
            )



