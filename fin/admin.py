from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
 
admin.site.register(client)
admin.site.register(Données)
admin.site.register(Facture)
admin.site.register(dataimport)
class Données(ImportExportModelAdmin):
    list_display = ('Nom','Date','Valuer')