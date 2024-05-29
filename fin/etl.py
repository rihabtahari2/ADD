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
    print(df)
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
    df = df.replace(r'[;*+_\'"=)(|{}!?#[\]].','', regex=True)
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

def load_from_facture(dataimport_instance, user_id):
    factures = Facture.objects.filter(fichier=dataimport_instance)
    
    # Charger les données de Dim_client_ent
    for client_ent_django in Dim_client_ent.objects.all():
        # Créer et sauvegarder chaque instance de Dimclient_ent
        dim_client_ent = Dimclient_ent(
            nom=client_ent_django.nom,
            Adresse=client_ent_django.Adresse,
            Activity=client_ent_django.Activity,
            email=client_ent_django.email
        )
        dim_client_ent.save()

    # Charger les données de Facture
    for facture_django in factures:
        # Créer et sauvegarder chaque instance de Dimfacture
        dim_facture = Dimfacture(
            num_fac=facture_django.numero_facture
        )
        dim_facture.save()

        # Créer et sauvegarder chaque instance de DimProduit
        dim_produit = DimProduit(
            libelle=facture_django.libelle,
            prix_unitaire=facture_django.prix_unitaire
        )
        dim_produit.save()

        # Créer et sauvegarder chaque instance de DimClient
        dim_client = DimClient(
            nom_client=facture_django.nom_client
        )
        dim_client.save()

        # Créer et sauvegarder chaque instance de DimFournisseur
        dim_fournisseur = DimFournisseur(
            nom_fournisseur=facture_django.nom_fournisseur
        )
        dim_fournisseur.save()

        # Conversion de la chaîne de date en datetime
        date_string = f"{facture_django.date}"  # Ajoutez une heure fixe pour éviter les erreurs de conversion
        date_facture = datetime.strptime(date_string, '%d/%m/%Y %H:%M:%S')

        # Extraire le jour, le mois et l'année
        jour = str(date_facture.day)
        mois = str(date_facture.month)
        annee = str(date_facture.year)

        # Créer et sauvegarder chaque instance de DimTemps
        dim_temps = DimTemps(
            id_Tempss=f"{jour}/{mois}/{annee}",
            jour=jour,
            mois=mois,
            annee=annee
        )
        dim_temps.save()

        if facture_django.catéogorie == 'Vente':
            # Créer et sauvegarder chaque instance de fait_vente
            fait_vente = faitvente(
                id_client=dim_client,
                id_produit=dim_produit,
                id_temps=dim_temps,
                client_ent=dim_client_ent,
                TVA=facture_django.tva,
                total_ttc=facture_django.total_ttc,
                total_hors_taxe=facture_django.total_hors_taxe,
                quantite=facture_django.quantite,
                CA=Decimal(facture_django.quantite) * facture_django.prix_unitaire.to_decimal(),
                id_fact=dim_facture,
                id_user=user_id  # Ajouter l'ID de l'utilisateur
            )
            fait_vente.save()
        elif facture_django.catéogorie == 'Achat':
            # Créer et sauvegarder chaque instance de fait_achat
            fait_achat = faitachat(
                id_produit=dim_produit,
                id_fournisseur=dim_fournisseur,
                id_temps=dim_temps,
                client_ent=dim_client_ent,
                TVA=facture_django.tva,
                total_ttc=facture_django.total_ttc,
                total_hors_taxe=facture_django.total_hors_taxe,
                quantite=facture_django.quantite,
                id_fact=dim_facture,
                id_user=user_id  # Ajouter l'ID de l'utilisateur
            )
            fait_achat.save()