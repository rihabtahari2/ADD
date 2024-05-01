from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from fin.models import *
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http.response import JsonResponse
from fin.serializers import ClientSerializer
from fin.resources import DonnéesResource
import csv,io
from .etl import transform, load
from .decorators import expert_required

import pandas as pd
from io import TextIOWrapper
from datetime import datetime


#from fin.forms import OrderForm
#from .filters import OrderFilter
# Create your views here.
def login(request):
    if request.method == 'POST':
        if 'add' in request.POST:
            nom = request.POST.get('Username')
            email = request.POST.get('Email')
            mot_de_passe = request.POST.get('Password')
            confirmation_mot_de_passe = request.POST.get('Confirm password')
            #user=omptable.objects.create(ComptableNom=nom, ComptableEmail=email, ComptablePassword=mot_de_passe)
            #user.save()
    
    return render(request,'pfe/login.html')

def login (request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authentification de l'assistant
        assistant = authenticate(request, username=username, password=password)

        if assistant is not None:
            auth_login(request, assistant)
            return redirect('home')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')

    return render(request, 'pfe/login.html') 
    

#@ login_required(login_url='singin')
def home(request):
    return render(request,'pfe/base.html')

def base (request):
    return render(request,'base.html')

def register(request):
    form=CreateUserform()
    if request.method == 'POST':
      form=CreateUserform(request.POST)
      if form.is_valid():
          user=form.save()
          username = form.cleaned_data.get('username')
          group = Group.objects.get(name='Experts')
          user.groups.add(group)
          messages.success(request,'Account was created for '+ username)

          return redirect('singin')
        
    context={'form':form}
    return render(request,'pfe/register.html',context)

def singin(request):
    if request.method == 'POST':
       nom = request.POST.get('username')
       password1 = request.POST.get('password')

       user = authenticate(request, username=nom, password=password1)

       if user is not None:
           auth_login(request, user)
           return redirect('Home')
       else:
           messages.info(request,'Username OR password is incorrect')
             
    context={}
    return render(request,'pfe/singin.html',context)

def logoutUser(request):
    logout(request)
    return redirect('singin')


def navbar(request):
    form = FichiersForm()
    if request.method == 'POST'and 'upload_file' not in request.POST:
        form = FichiersForm(request.POST, request.FILES)  # Inclure les fichiers dans la requête POST
        if form.is_valid():
            selected_client_name = form.cleaned_data['client']
            selected_client = client.objects.get(clientName=selected_client_name)
            
            # Créer une instance de dataimport avec les détails du formulaire
            dataimport_instance = form.save(commit=False)
            # Assigner l'objet client récupéré à l'instance de dataimport
            dataimport_instance.client = selected_client
            # Enregistrer l'instance de dataimport
            dataimport_instance.save()
            dataimport_instance = form.save()  # Enregistrer les détails du fichier
            myfile = request.FILES['myfile']  # Accéder au fichier soumis
            data = pd.read_csv(myfile,encoding='ISO-8859-1')  # Lire les données CSV
            transformed_data = transform(data)  # Transformer les données
            load(transformed_data,  dataimport_instance )
            return HttpResponse("fffff")
    fichiers=dataimport.objects.all()
    context = {'form': form,'fichiers':fichiers}
    return render(request, 'navbar1.html', context)



def navbar1 (request):
    return render(request,'index1.html')
@expert_required
def list_client(request):
     # Vérifier si l'utilisateur appartient au groupe "Expert"
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    clients = client.objects.all()
    clients = client.objects.order_by('clientId')
    paginator = Paginator(clients, 8)  # Paginer les clients avec 8 clients par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pfe/client.html', {'page_obj': page_obj, 'clients': page_obj.object_list,'user_is_expert': user_is_expert})
@expert_required
def add_client(request):
     # Vérifier si l'utilisateur appartient au groupe "Expert"
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    form = ClientForm()
    if request.method == 'POST':
        form = ClientForm(request.POST)  
        if form.is_valid():
            Client=client(
                clientName=form.cleaned_data['clientName'],
                clientAdresse=form.cleaned_data['clientAdresse'],
                clientActivity=form.cleaned_data['clientActivity'],
                id_user=form.cleaned_data['id_user']
            )
            Client.save()
            return redirect('client')
    context = {'form': form,'user_is_expert': user_is_expert}
    return render(request, 'pfe/add_client.html', context)
@expert_required
def update_client(request, pk):
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    Client = client.objects.get(clientId=pk)
    form = ClientForm(instance=Client)
    if request.method == 'POST':
        form = ClientForm(request.POST,instance=Client )  
        if form.is_valid():
            form.save()
            return redirect('client')

    context={'form': form,'user_is_expert': user_is_expert}
    return render(request, 'pfe/add_client.html', context)

def delete_client(request,pk):
    if request.method == 'POST':
        client_instance = client.objects.get(clientId=pk)
        client_instance.delete()
        return redirect('client')
    else:
        # Si la requête n'est pas de type POST, retourner une réponse 405 Méthode non autorisée
        return HttpResponse(status=405)
    
def expl (request):
    clients = client.objects.all()
    context = {'clients': clients}
    return render(request,'pfe/exple.html', context)

def expl1 (request):
   clients = client.objects.all()
   paginator = Paginator(clients, 8)  # Paginer les clients avec 5 clients par page
   page_number = request.GET.get('page')
   page_obj = paginator.get_page(page_number)
   return render(request,'pfe/expl1.html',{'page_obj': page_obj, 'clients': page_obj.object_list})
@expert_required 
def list_assistant(request):
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    assistants_group = Group.objects.get(name='Assistants')
    utilisateurs = User.objects.filter(groups=assistants_group)
    utilisateurs_info = [] 
    for utilisateur in utilisateurs:
        info_utilisateur = {
            'username': utilisateur.username,
            'email': utilisateur.email,
            'date_creation': utilisateur.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': utilisateur.last_login.strftime('%Y-%m-%d %H:%M:%S') if utilisateur.last_login else None  
        }
        utilisateurs_info.append(info_utilisateur)

    paginator = Paginator( utilisateurs_info, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pfe/assistant.html', {'page_obj': page_obj, 'utilisateurs_info': page_obj.object_list,'user_is_expert': user_is_expert})
from django.core.mail import EmailMessage
import smtplib

@expert_required
def add_assistant(request):
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    form = CreateUserform()

    if request.method == 'POST':
        form = CreateUserform(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='Assistants')
            user.groups.add(group)
            messages.success(request, 'Account was created for ' + username)

            selected_clients = request.POST.getlist('clients')

            # Associer les clients à l'utilisateur
            for client_id in selected_clients:
                client_instance = client.objects.get(pk=client_id)
                UserClient.objects.create(user=user, client=client_instance)

            # Envoi de l'e-mail
            subject = 'Création de compte'
            message = f"Bonjour,\n\nVoici vos informations d'identification pour accéder à l'application IntelliCount :\n\nNom d'utilisateur : {user.username}\nMot de passe : {form.cleaned_data.get('password1')}\n\nVous pouvez accéder à l'application en suivant ce lien : http://127.0.0.1:8000/ \n\n\n Cordialement,\n Elite Council Consulting "

            email = EmailMessage(
                subject,
                message,
                to=[form.cleaned_data.get('email')],
            )
            email.send()

            return redirect('assistant')
    context = {'form': form, 'user_is_expert': user_is_expert}
    return render(request, 'pfe/add_assistant.html', context)
@expert_required
def updateassistant(request, pk):
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    user = User.objects.get(id=pk)
    if request.method == 'POST':
        form = CreateUserform(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirigez vers la page d'accueil ou une autre vue
    else:
        form = CreateUserform(instance=user)
    return render(request, 'pfe/add_assistant.html', {'form': form,'user_is_expert': user_is_expert})
@ login_required(login_url='singin')
def home_page(request):
    # Vérifier si l'utilisateur appartient au groupe "Expert"
    user_is_expert = request.user.groups.filter(name='Experts').exists()

    # Votre logique existante pour le traitement du formulaire et la récupération des fichiers
    form = FichiersForm()
    fichier_id = None
    if request.method == 'POST' and 'upload_file' not in request.POST:
        form = FichiersForm(request.POST, request.FILES)
        if form.is_valid():
            selected_client_name = form.cleaned_data['client']
            selected_client = client.objects.get(clientName=selected_client_name)
            dataimport_instance = form.save(commit=False)
            dataimport_instance.client = selected_client
            dataimport_instance.save()

            fichier_id = dataimport_instance.Id
            myfile = request.FILES['myfile']
            data = pd.read_csv(myfile, encoding='ISO-8859-1').rename(columns=lambda x: x.lower())
            transformed_data = transform(data)
            load(transformed_data, dataimport_instance)
            return redirect('données', fichier_id=fichier_id)  

    fichiers = dataimport.objects.all()
    context = {'form': form, 'fichiers': fichiers, 'fichier_id': fichier_id, 'user_is_expert': user_is_expert}

    return render(request, 'pfe/home.html', context)


def client_assistant(request,pk):
    assistant = User.objects.get(id=pk)
    clients_disponibles = client.objects.all()
    return render(request, 'pfe/client_assistant.html',{'assistant': assistant, 'clients_disponibles': clients_disponibles})


from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
import json

def donn(request, fichier_id):
    fichiers = dataimport.objects.get(pk=fichier_id)
    
    # Récupérer toutes les factures associées à ce fichier spécifique
    factures = Facture.objects.filter(fichier=fichiers) 

    # Convertir les objets Decimal128 en nombres Python
    data = [
        {
            'date': facture.date,
            'numero_facture': facture.numero_facture,
            'nom_fournisseur': facture.nom_fournisseur,
            'nom_client': facture. nom_client,
            'libelle': facture.libelle,
            'prix_unitaire': float(str(facture.prix_unitaire)),
            'quantite': facture.quantite,
            'tva': float(str(facture.tva)),
            'total_hors_taxe': float(str(facture.total_hors_taxe)),
            'total_ttc': float(str(facture.total_ttc)),
            'catéogorie': facture.catéogorie ,
        }
        for facture in factures
    ]

    # Convertir les données en format JSON
    data_json = json.dumps(data, cls=DjangoJSONEncoder)

    return render(request, 'pfe/donneés.html', {'data': data_json, 'fichiers':fichiers,'fichier_id': fichier_id})
from django.http import HttpResponseRedirect
def import_data(request, fichier_id):
    if request.method == 'POST' and request.FILES.get('file'):
        myfile = request.FILES['file']
        try:
            # Charger les données du fichier CSV
            data = pd.read_csv(myfile, encoding='ISO-8859-1').rename(columns=lambda x: x.lower())
            # Transformer les données si nécessaire
            transformed_data = transform(data)
            # Récupérer l'instance dataimport correspondant à l'ID passé en paramètre
            fichier_instance = dataimport.objects.get(pk=fichier_id)
            # Appeler la fonction load_data pour enregistrer les données
            load_data(transformed_data, fichier_instance)
            # Retourner une réponse JSON indiquant le succès
            messages.success(request,"Les données ont été importées avec succès ! ")
            return JsonResponse({'success': True, 'message': "Les données ont été importées avec succès !"})
        except Exception as e:
            # En cas d'erreur, ajouter un message d'erreur
            return JsonResponse({'success': False, 'message': "Une erreur s'est produite lors de l'importation des données."})
    else:
        return JsonResponse({'success': False, 'message': "Aucun fichier n'a été reçu."})
    
def load_data(data, fichier_instance):
    for index, row in data.iterrows():
        # Créer une instance de Facture en associant l'instance de dataimport passée en paramètre
        facture = Facture(fichier=fichier_instance, Date=row['Date'], numero_facture=row['Numéro de facture'],
                           nom_fournisseur=row['Nom du fournisseur'], nom_client=row['Nom du client'],
                           libelle=row['Libellé'], prix_unitaire=row['Prix unitaire'], total_ttc=row['Total TTC'],
                           total=row['Total'], quantite=row['Quantité'], tva=row['TVA'],
                           total_hors_taxe=row['Total hors taxe'], catéogorie=row['Catégorie'])
        # Enregistrer la facture dans la base de données
        facture.save()

def save_data(request):
    if request.method == 'POST' and request.is_ajax():
        try:
            modifications = request.POST.get('modifications')
            modifications = json.loads(modifications)
            
            for modification in modifications:
                row = modification['row']
                col = modification['col']
                new_value = modification['newValue']
                
                # Mettre à jour l'instance de Facture correspondante
                facture = Facture.objects.get(id=row)
                if col == 1:  # Colonne 'Date'
                    facture.date = new_value
                elif col == 2:  # Colonne 'Numéro de facture'
                    facture.numero_facture = new_value
                # Continuez pour les autres colonnes...

                facture.save()
            
            return JsonResponse({'message': 'Modifications enregistrées avec succès'}, status=200)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)


import matplotlib.pyplot as plt
import io
import base64
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from decimal import Decimal
from collections import Counter
from collections import defaultdict
from decimal import Decimal
from bson.decimal128 import Decimal128
from bson import json_util
import json

def dashboard(request):
    dataimport_id = request.GET.get('dataimport_id')  # Récupérer l'ID depuis la requête GET
    fichier_id = request.GET.get('fichier_id')
    if dataimport_id:
        try:
            dataimport_instance = dataimport.objects.get(pk=dataimport_id)
            factures = Facture.objects.filter(fichier=dataimport_instance)
            # Par exemple, récupérez les factures associées à cet objet dataimport
            factures = Facture.objects.filter(fichier=dataimport_instance)
            # Calculer le nombre total de factures
            nombre_factures = factures.count()
            nombre_fournisseurs = len(set(facture.nom_fournisseur for facture in factures))
            nombre_clients = len(set(facture.nom_client for facture in factures))
            nombre_achats = factures.filter(catéogorie='Achat').count()
            nombre_ventes = factures.filter(catéogorie='Vente').count()
            Total1=nombre_ventes-nombre_achats
            
            # Calculer le revenu total
            total_revenue = sum(Decimal(str(facture.total_ttc)) for facture in factures if facture.catéogorie== 'Vente') - sum(Decimal(str(facture.total_ttc)) for facture in factures if facture.catéogorie== 'Achat')
            
            # Comptage du nombre de fois que chaque produit apparaît dans la facture
            total_produits = 0
            produits_counter = defaultdict(int)

            for facture in factures:
                for produit in facture.libelle.split(', '):
                    produits_counter[produit] += 1
                    total_produits += 1

            resultats_de_revenue_par_produit = [(produit, (count / total_produits) * 100) for produit, count in produits_counter.items()]
            # Afficher le CA par mois 
            ca_par_mois = []
            labels1 = []

            nom_mois = {
                1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
                5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
                9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
            }

            for i in range(1, 13):
                ventes_mois = Decimal(0)
                achats_mois = Decimal(0)
                
                # Filtrer les factures pour le mois en cours
                factures_mois = factures.filter(date__icontains=f"{i:02d}/")
                
                for facture in factures_mois:
                    if facture.catéogorie == 'Vente':
                        ventes_mois += Decimal(str(facture.total_ttc))
                    elif facture.catéogorie == 'Achat':
                        achats_mois += Decimal(str(facture.total_ttc))
                
                # Calculer le chiffre d'affaires pour le mois en cours
                ca_mois = ventes_mois - achats_mois
                ca_par_moiss = f" {ca_mois}"
                ca_par_mois.append(ca_par_moiss)
                # Ajouter le nom du mois et son chiffre d'affaires correspondant à la liste
                label_mois = f"{nom_mois.get(i)} "
                labels1.append(label_mois)

            # Calculer la croissance historique moyenne
            croissance_moyenne = (total_revenue / nombre_factures) if nombre_factures > 0 else Decimal(0)
            
            # Prédire le chiffre d'affaires pour l'année suivante
            chiffre_affaires_previsionnel = []
            for mois in range(1, 13):
                # Appliquer la croissance moyenne pour prédire le chiffre d'affaires pour chaque mois
                chiffre_affaires_previsionnel_mois = total_revenue + (croissance_moyenne * mois)
                ca_par_mois_pré = f" {chiffre_affaires_previsionnel_mois}"
              
                chiffre_affaires_previsionnel.append(ca_par_mois_pré)
            # Créer les étiquettes pour les mois de l'année suivante
            labels_mois_suivant = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            ventes_par_mois = {}
            achats_par_mois = {}

            # Parcourir les factures et traiter les dates
            for facture in factures:
                date_facture = datetime.strptime(facture.date, '%d/%m/%Y %H:%M:%S')
                mois = date_facture.month
                
                # Mettre à jour les ventes par mois
                if facture.catéogorie == 'Vente':
                    ventes_par_mois[mois] = ventes_par_mois.get(mois, 0) + 1               
                # Mettre à jour les achats par mois
                elif facture.catéogorie== 'Achat':
                    achats_par_mois[mois] = achats_par_mois.get(mois, 0) + 1
            ventes_par_mois_list = [ventes_par_mois.get(mois, 0) for mois in range(1, 13)]
            achats_par_mois_list = [achats_par_mois.get(mois, 0) for mois in range(1, 13)]
            # Convertir les listes en chaînes JSON
            ventes_json = json.dumps(ventes_par_mois_list)
            achats_json = json.dumps(achats_par_mois_list)
            #//////////////////////////////CA par mois////////////////////////////////////////////////
            ventes = factures.filter(catéogorie='Vente')
            # Initialiser un dictionnaire pour stocker le chiffre d'affaires total par mois
            chiffre_affaires_par_mois = defaultdict(Decimal)
            # Parcourir toutes les ventes
            for vente in ventes:
                # Extraire le mois de la date de la vente
                date_vente = datetime.strptime(vente.date, '%d/%m/%Y %H:%M:%S')
                mois = date_vente.month
                # Calculer le chiffre d'affaires de la vente (prix de vente x quantité vendue)
                chiffre_affaire_vente = float(str(vente.prix_unitaire)) * vente.quantite
                # Convertir le chiffre d'affaires de la vente en Decimal
                chiffre_affaire_vente_decimal = Decimal(chiffre_affaire_vente)
                # Ajouter le chiffre d'affaires de la vente au chiffre d'affaires total du mois correspondant
                chiffre_affaires_par_mois[mois] += chiffre_affaire_vente_decimal
            # Convertir le dictionnaire en une liste de chiffres d'affaires totaux
            chiffre_affaires_liste = [float(chiffre_affaires_par_mois[mois]) for mois in range(1, 13)]
            #////////////////////////////////////////////////////////////////////////////////////////////
            #***********************CA prévision*********************************************************
            # Facteur de croissance prévu pour l'année suivante (par exemple, 10% de croissance)
            facteur_croissance = Decimal('1.20')

            # Calcul du chiffre d'affaires prévisionnel pour l'année suivante
            chiffre_affaires_previsionnel_annee_suivante = []
            for chiffre_affaire in chiffre_affaires_liste:
                chiffre_affaire_decimal = Decimal(str(chiffre_affaire))  # Convertir en Decimal
                chiffre_affaire_previsionnel = chiffre_affaire_decimal * facteur_croissance
                chiffre_affaires_previsionnel_annee_suivante.append(chiffre_affaire_previsionnel)

            # Affichage des chiffres d'affaires prévisionnels pour chaque mois de l'année suivante
            for mois, chiffre_affaire_previsionnel in enumerate(chiffre_affaires_previsionnel_annee_suivante, start=1):
                print(f"Mois {mois}: {chiffre_affaire_previsionnel}")
            chiffre_affaire_previsionnel = chiffre_affaires_previsionnel_annee_suivante
            #*************************************************************************************************
            #""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            chiffre_affaires_par_produit_par_mois = defaultdict(lambda: defaultdict(Decimal))

            # Parcourir toutes les ventes
            for vente in ventes:
                # Extraire le mois de la date de la vente
                date_vente = datetime.strptime(vente.date, '%d/%m/%Y %H:%M:%S')
                mois = date_vente.month

                # Calculer le chiffre d'affaires de la vente pour ce produit (prix de vente x quantité vendue)
                chiffre_affaire_produit = Decimal(str(vente.prix_unitaire)) * vente.quantite

                # Ajouter le chiffre d'affaires de la vente pour ce produit au chiffre d'affaires total du mois correspondant
                chiffre_affaires_par_produit_par_mois[mois][vente.libelle] += chiffre_affaire_produit

            # Afficher le chiffre d'affaires total par produit pour chaque mois
            for mois, chiffre_affaires_par_produit in chiffre_affaires_par_produit_par_mois.items():
                print(f"Mois {mois}:")
                for produit, chiffre_affaire_total in chiffre_affaires_par_produit.items():
                    print(f"- Produit {produit}: {chiffre_affaire_total}")
            context = {
                'chiffre_affaire_total':chiffre_affaire_total,
                'produit':produit,
                'dataimport_instance': dataimport_instance,
                'factures': factures,
                'nombre_factures': nombre_factures,
                'nom_client': dataimport_instance.client.clientName,
                'nombre_fournisseurs': nombre_fournisseurs,
                'nombre_clients': nombre_clients,
                'nombre_achats': nombre_achats,
                'nombre_ventes': nombre_ventes,
                'ventes_par_mois': ventes_json,
                'achats_par_mois':achats_json,
                'total_revenue': total_revenue,
                'resultats_de_revenue_par_produit': resultats_de_revenue_par_produit,
                'ca_par_mois': ca_par_mois,
                'labels1': labels1,
                'chiffre_affaires_previsionnel': chiffre_affaires_previsionnel,
                'labels_mois_suivant': labels_mois_suivant,
                'fichier_id':fichier_id,
                'dataimport_id':dataimport_id,
                'chiffre_affaires_liste':chiffre_affaires_liste,
                'chiffre_affaire_previsionnel':chiffre_affaire_previsionnel,
                
            }
            return render(request, 'pfe/dashboard.html', context)
        except dataimport.DoesNotExist:
            return HttpResponse("Dataimport avec cet ID non trouvé.", status=404)
    else:
        return HttpResponse("ID de dataimport vide.", status=400)
import os
import matplotlib.pyplot as plt
from django.conf import settings
from django.http import HttpResponse
from django.template import Context, loader

def test(request):

    return render(request, 'test.html')
from django.http import JsonResponse
from .models import Facture

def import_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        myfile = request.FILES['file']
        try:
            # Lire les données CSV
            data = pd.read_csv(myfile, encoding='ISO-8859-1').rename(columns=lambda x: x.lower())
            # Transformer les données (vous devez définir cette fonction)
            transformed_data = transform(data)
            print(transformed_data)
            # Retourner une réponse JSON indiquant le succès
            return JsonResponse({'success': True})
        except Exception as e:
            # En cas d'erreur, retourner une réponse JSON avec l'erreur
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # Si aucun fichier n'a été reçu, retourner une réponse JSON indiquant l'erreur
        return JsonResponse({'success': False, 'error': 'Aucun fichier n\'a été reçu.'})


# views.py
from django.template.loader import render_to_string
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def export_csv(request, dataimport_id):
    # Récupérer les données à exporter en CSV
    fichiers = dataimport.objects.get(pk=dataimport_id)
    factures = Facture.objects.filter(fichier=fichiers)

    # Préparer les données au format CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Numero de Facture', 'Nom du Fournisseur', 'Nom du Client', 'Libelle', 'Prix Unitaire', 'Quantite', 'TVA', 'Total HT', 'Total TTC', 'Catégorie'])

    for facture in factures:
        writer.writerow([facture.date, facture.numero_facture, facture.nom_fournisseur, facture.nom_client, facture.libelle, facture.prix_unitaire, facture.quantite, facture.tva, facture.total_hors_taxe, facture.total_ttc, facture.catéogorie])

    return response
def export_pdf(request):
    dataimport_id = request.GET.get('dataimport_id')  # Récupérer dataimport_id depuis la requête GET
    if dataimport_id:
        fichiers = dataimport.objects.get(pk=dataimport_id)
        factures = Facture.objects.filter(fichier=fichiers)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="export.pdf"'
        
        data = [[facture.date, facture.numero_facture, facture.nom_fournisseur, facture.nom_client, facture.libelle, facture.prix_unitaire, facture.quantite, facture.tva, facture.total_hors_taxe, facture.total_ttc, facture.categorie] for facture in factures]

        pdf = SimpleDocTemplate(response, pagesize=letter)
        table = Table(data)
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(style)
        pdf.build([table])
        
        return response
    else:
        # Gérer le cas où dataimport_id n'est pas fourni
        return HttpResponse("Dataimport ID is missing.", status=400)
   