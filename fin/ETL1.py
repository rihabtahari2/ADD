import petl as etl
from fin.models import *
from datetime import datetime

def extract(file_path):
    table = etl.fromcsv(file_path)
    table = etl.convert(table, 'date', lambda d: datetime.strptime(d, '%d/%m/%Y'))
    table = etl.convert(table, 'time', lambda t: datetime.strptime(t, '%H:%M:%S').time())
    return table

def transform1(table):
    for row in table:
        # Transformation pour la dimension Produit
        produit, _ = DimProduit.objects.get_or_create(libelle=row['Libellé'], prix_unitaire=row['Prix unitaire'])
        
        # Transformation pour la dimension Client
        client, _ = DimClient.objects.get_or_create(nom_client=row['Nom du client'])
        
        # Transformation pour la dimension Fournisseur
        fournisseur, _ = DimFournisseur.objects.get_or_create(nom_fournisseur=row['Nom du fournisseur'])
        
        # Transformation pour la dimension Temps
        temps, _ = DimTemps.objects.get_or_create(mois=row['date'].month, annee=row['date'].year)
        
        # Chargement dans le fait LigneFacture
        ligne_facture = LigneFacture.objects.create(
            id_client=client,
            id_produit=produit,
            id_fournisseur=fournisseur,
            id_temps=temps,
            TVA=row['TVA'],
            total_ttc=row['Total TTC'],
            total_hors_taxe=row['Total hors taxe'],
            quantite=row['Quantité']
        )
        ligne_facture.save()
