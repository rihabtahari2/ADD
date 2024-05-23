from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
 
admin.site.register(client)
admin.site.register(Données)
admin.site.register(Facture)
admin.site.register(dataimport)
admin.site.register(Dim_Produit)
admin.site.register(Dim_Temps)
admin.site.register(Dim_Client)
admin.site.register(fait_vente)
admin.site.register(fait_achat)
admin.site.register(Dim_Fournisseur)
admin.site.register(Dim_client_ent)
admin.site.register(Dim_facture)


class Données(ImportExportModelAdmin):
    list_display = ('Nom','Date','Valuer')