from django.http import HttpResponse, HttpResponseBadRequest
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
          ExpertProfile.objects.create(user=user)
          username = form.cleaned_data.get('username')
          group = Group.objects.get(name='Experts')
          user.groups.add(group)
          messages.success(request, 'Account was created for ' + username, extra_tags='register_success')

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
    # Vérifiez si l'utilisateur appartient au groupe "Expert"
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    
    # Si l'utilisateur est un expert, récupérez uniquement les clients associés à son profil
    if user_is_expert:
        expert_profile = ExpertProfile.objects.get(user=request.user)
        clients = client.objects.filter(Expertprofile=expert_profile)

    else:
        # Si l'utilisateur n'est pas un expert, récupérez tous les clients
        clients = client.objects.all()
    # Ajoutez les noms d'utilisateur associés à chaque client
    for client_obj in clients:
        user_client = UserClient.objects.filter(client=client_obj).first()
        if user_client:
            client_obj.username = user_client.user.username
        else:
            client_obj.username = None
    # Paginez les clients avec 8 clients par page
    paginator = Paginator(clients, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pfe/client.html', {'page_obj': page_obj, 'clients': page_obj.object_list, 'user_is_expert': user_is_expert})
@expert_required
def add_client(request):
    # Vérifiez si l'utilisateur appartient au groupe "Expert"
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    form = ClientForm()
    if request.method == 'POST':
        form = ClientForm(request.POST)  
        if form.is_valid():
            # Créez une instance du client, mais ne la sauvegardez pas encore dans la base de données
            client_instance = form.save(commit=False)
            
            # Récupérez l'objet ExpertProfile associé à l'utilisateur actuel
            expert_profile = ExpertProfile.objects.get(user=request.user)
            
            # Associez le client à l'ExpertProfile
            client_instance.Expertprofile = expert_profile
            
            # Sauvegardez le client dans la base de données
            client_instance.save()
            
            return redirect('client')
    context = {'form': form, 'user_is_expert': user_is_expert}
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

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('assistant') # Redirection vers la page des assistants après la suppression
    else:
        return HttpResponse(status=405)
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
    expert_profile = ExpertProfile.objects.get(user=request.user)
    assistants = AssistantProfile.objects.filter(expert_profile=expert_profile)
    paginator = Paginator(assistants, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    context = {'page_obj': page_obj,'assistants': assistants, 'user_is_expert': user_is_expert}
    return render(request, 'pfe/assistant.html', context)
from django.core.mail import EmailMessage
import smtplib

@expert_required
def add_assistant(request):
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    form = CreateUserform()
    # Si c'est une requête GET, récupérer les clients associés à l'expert connecté
    expert_profile = ExpertProfile.objects.get(user=request.user)
    expert_clients = client.objects.filter(Expertprofile=expert_profile)
    if request.method == 'POST':
        form = CreateUserform(request.POST)
        if form.is_valid():
            user = form.save()
            assistant_profile = AssistantProfile.objects.create(user=user)

            # Récupérer l'expert correspondant à l'utilisateur connecté
            expert_profile = ExpertProfile.objects.get(user=request.user)

            # Associer l'assistant à son expert
            assistant_profile.expert_profile = expert_profile
            assistant_profile.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='Assistants')
            user.groups.add(group)

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
    context = {'form': form, 'user_is_expert': user_is_expert,'expert_clients': expert_clients}
    return render(request, 'pfe/add_assistant.html', context)
@expert_required
def update_assistant(request, pk):
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    expert_profile = ExpertProfile.objects.get(user=request.user)
    expert_clients = client.objects.filter(Expertprofile=expert_profile)
    # Récupérer l'assistant à partir de son ID
    assistant = User.objects.get(id=pk)
    
    if request.method == 'POST':
        # Mettre à jour les informations de l'assistant avec les données du formulaire
        form = CreateUserform(request.POST, instance=assistant)
        if form.is_valid():
            form.save()
            return redirect('assistant')  # Rediriger vers la liste des assistants après la mise à jour
    else:
        form = CreateUserform(instance=assistant)  # Pré-remplir le formulaire avec les informations actuelles de l'assistant
    
    context = {'form': form, 'user_is_expert': user_is_expert,'expert_clients': expert_clients}
    return render(request, 'pfe/update_assistant.html', context)
@ login_required(login_url='singin')
def home_page(request):
    # Vérifier si l'utilisateur appartient aux groupes "Experts" ou "Assistants"
    user_is_expert = request.user.groups.filter(name='Experts').exists()
    user_is_assistant = request.user.groups.filter(name='Assistants').exists()
    
    expert_clients = None
    if user_is_expert:
        # Si l'utilisateur est un expert, récupérer les clients associés
        expert_profile = ExpertProfile.objects.get(user=request.user)
        expert_clients = client.objects.filter(Expertprofile=expert_profile)
    elif user_is_assistant:
        # Si l'utilisateur est un assistant ou un expert_client, récupérer les clients affectés
        expert_clients = client.objects.filter(userclient__user=request.user)
    # Votre logique existante pour le traitement du formulaire et la récupération des fichiers
    form = FichiersForm()
    fichier_id = None
    if request.method == 'POST' and 'upload_file' not in request.POST:
        form = FichiersForm(request.POST, request.FILES)
        if form.is_valid():
            selected_client_name = form.cleaned_data['client']
            selected_client = client.objects.get(clientName=selected_client_name)
            dim_client_ent, _ = Dim_client_ent.objects.get_or_create(
                nom=selected_client.clientName,
                Adresse=selected_client.clientAdresse,
                Activity=selected_client.clientActivity,
                email=selected_client.contact
            )
            # Créez une instance de dataimport, mais ne la sauvegardez pas encore dans la base de données
            dataimport_instance = form.save(commit=False)
            
            # Récupérez le profil de l'utilisateur actuel
            if user_is_expert:
                dataimport_instance.Expertprofile = ExpertProfile.objects.get(user=request.user)
            else:
                dataimport_instance.Assistantprofile = AssistantProfile.objects.get(user=request.user)
            
            dataimport_instance.client = selected_client
            dataimport_instance.save()

            fichier_id = dataimport_instance.Id
            # charger les données csv
            myfile = request.FILES['myfile']
            if myfile.name.endswith('.csv'):
                # Si c'est un fichier CSV, procédez au traitement
                data = pd.read_csv(myfile, encoding='ISO-8859-1').rename(columns=lambda x: x.lower())
                transformed_data = transform(data)
                load(transformed_data, dataimport_instance,dim_client_ent)
                return redirect('données', fichier_id=fichier_id)
            else:
                # Si ce n'est pas un fichier CSV, renvoyez un message d'erreur
                return HttpResponseBadRequest("Le fichier téléchargé n'est pas un fichier CSV.")
             

    # Récupérez les dataimport associés au profil de l'utilisateur actuel
    if user_is_expert:
        fichiers = dataimport.objects.filter(Expertprofile__user=request.user)
    else:
        fichiers = dataimport.objects.filter(Assistantprofile__user=request.user)

    context = {'form': form, 'fichiers': fichiers, 'fichier_id': fichier_id, 'user_is_expert': user_is_expert,'expert_clients': expert_clients}
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
        produit, _ = Dim_Produit.objects.get_or_create(
            libelle=row['Libellé'],
            defaults={'prix_unitaire': row['Prix unitaire']}
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

            # les jointure
            # Créer une instance de fait_vente en utilisant les instances récupérées
            nouvelle_vente = fait_vente.objects.create(
                id_client=client,
                id_produit=produit,
                id_temps=temps,
                TVA=row['TVA'],
                total_ttc=row['Total TTC'],
                total_hors_taxe=row['Total hors taxe'],
                quantite=row['Quantité']
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
                TVA=row['TVA'],
                total_ttc=row['Total TTC'],
                total_hors_taxe=row['Total hors taxe'],
                quantite=row['Quantité']
            )

        facture = Facture(fichier= fichier_instance ,date=row['Date1'], numero_facture=row['Numéro de facture'],
                           nom_fournisseur=row['Nom du fournisseur'], nom_client=row['Nom du client'],
                         libelle=row['Libellé'],prix_unitaire=row['Prix unitaire'],total_ttc=row['Total TTC'],
                         quantite=row['Quantité'],tva=row['TVA'],
                         total_hors_taxe=row['Total hors taxe'],catéogorie=row['Catégorie'])
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
import json
import decimal
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
            #////////////////////////produit par vente////////////////////////////////////
            # Récupérer les factures de vente
            factures_vente = Facture.objects.filter(catéogorie='Vente')
            # Initialiser un dictionnaire pour stocker les totaux TTC par produit
            totals_par_produit = {}

            # Parcourir les factures de vente
            for facture in factures_vente:
                libelle = facture.libelle
                total_ttc = decimal.Decimal(str(facture.total_ttc))
                # Vérifier si le produit est déjà dans le dictionnaire
                if libelle in totals_par_produit:
                    # Si oui, ajouter le total TTC au total existant
                    totals_par_produit[libelle] += total_ttc
                else:
                    # Sinon, initialiser le total TTC pour ce produit
                    totals_par_produit[libelle] = total_ttc
            produits_ttc = []

            # Parcourir les totaux par produit
            for libelle, total_ttc in totals_par_produit.items():
                produits_ttc.append((libelle, total_ttc))
            #////////////////////////////////////////////////////////////////////////////////
            #////////////////////////produit par achat////////////////////////////////////
            # Récupérer les factures de vente
            factures_vente = Facture.objects.filter(catéogorie='Achat')
            # Initialiser un dictionnaire pour stocker les totaux TTC par produit
            totals_par_produit1 = {}

            # Parcourir les factures de vente
            for facture in factures_vente:
                libelle = facture.libelle
                total_ttc = decimal.Decimal(str(facture.total_ttc))
                # Vérifier si le produit est déjà dans le dictionnaire
                if libelle in totals_par_produit1:
                    # Si oui, ajouter le total TTC au total existant
                    totals_par_produit1[libelle] += total_ttc
                else:
                    # Sinon, initialiser le total TTC pour ce produit
                    totals_par_produit1[libelle] = total_ttc
            produits_ttc1 = []

            # Parcourir les totaux par produit
            for libelle, total_ttc in totals_par_produit1.items():
                produits_ttc1.append((libelle, total_ttc))
            #////////////////////////////////////////////////////////////////////////////////
            context = {
                'produits_ttc1': produits_ttc1,
                'produits_ttc': produits_ttc,
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
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
def export_csv(request):
    dataimport_id = request.GET.get('dataimport_id')
    if dataimport_id:
        fichiers = dataimport.objects.get(pk=dataimport_id)
        factures_achat = Facture.objects.filter(fichier=fichiers, catéogorie='Achat')
        factures_vente = Facture.objects.filter(fichier=fichiers, catéogorie='Vente')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Numero de Facture', 'Nom du Fournisseur', 'Nom du Client', 'Libelle', 'Prix Unitaire', 'Quantite', 'TVA', 'Total HT', 'Total TTC', 'Catégorie'])

        def parse_date(date_str):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y %H:%M:%S'):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    pass
            raise ValueError(f"No valid date format found for {date_str}")

        def group_and_write_totals(writer, factures):
            grouped = {}
            for facture in factures:
                facture_date = parse_date(facture.date)
                month = facture_date.strftime('%Y-%m')
                if month not in grouped:
                    grouped[month] = []
                grouped[month].append(facture)

            for month, factures in grouped.items():
                for facture in factures:
                    writer.writerow([
                        facture.date, facture.numero_facture, 
                        facture.nom_fournisseur, facture.nom_client, 
                        facture.libelle, Decimal(str(facture.prix_unitaire)), 
                        facture.quantite, facture.tva, 
                        Decimal(str(facture.total_hors_taxe)), 
                        Decimal(str(facture.total_ttc)), 
                        facture.catéogorie
                    ])
                total_ttc = sum(Decimal(str(f.total_ttc)) for f in factures)
                writer.writerow([
                    '', '', '', '', '', '', '', '', '', 
                    'Total ' + calendar.month_name[int(month.split('-')[1])], total_ttc
                ])

        writer.writerow(['Factures d\'Achat'])
        group_and_write_totals(writer, factures_achat)
        
        writer.writerow([])  # Ligne vide pour séparer les sections

        writer.writerow(['Factures de Vente'])
        group_and_write_totals(writer, factures_vente)

        return response
    else:
        return HttpResponse("ID de dataimport manquant.", status=400)
from reportlab.platypus import Spacer
import calendar
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
def export_pdf(request):
    dataimport_id = request.GET.get('dataimport_id')
    if dataimport_id:
        fichiers = dataimport.objects.get(pk=dataimport_id)
        factures_achat = Facture.objects.filter(fichier=fichiers, catéogorie='Achat')
        factures_vente = Facture.objects.filter(fichier=fichiers, catéogorie='Vente')
        client_name = fichiers.client.clientName
        addresse_client=fichiers.client.clientAdresse
        activity_client=fichiers.client.clientActivity
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="rapport_financier.pdf"'
        title_text = "Rapport Financier Annuel"
        title_style = getSampleStyleSheet()['Title']
        title = Paragraph(title_text, title_style)

        pdf = SimpleDocTemplate(response, pagesize=letter)
        elements = [title]
        # Spacer pour déplacer les éléments vers la droite
        spacer_width = 2 * inch  # Largeur du spacer en pouces (ajustée)
        elements.append(Spacer(spacer_width, 1))
        # Ajouter les détails du client à l'extrémité gauche de la page
        client_details_text = f"Client: {client_name}<br/>Adresse: {addresse_client}<br/>Activité: {activity_client}"
        client_details_style = getSampleStyleSheet()['Heading5']
        client_details_paragraph = Paragraph(client_details_text, client_details_style)
        elements.append(client_details_paragraph)

        # Convertir les valeurs total_ttc en Decimal
        total_revenue = sum(Decimal(str(facture.total_ttc)) for facture in factures_vente) - sum(Decimal(str(facture.total_ttc)) for facture in factures_achat)
        total_revenue_text = f"Le revenu total : {total_revenue} DT"
        total_revenue_style = getSampleStyleSheet()['Heading3']
        total_revenue_paragraph = Paragraph(total_revenue_text, total_revenue_style)
        elements.append(total_revenue_paragraph)
    
        ca = sum(Decimal(str(f.prix_unitaire)) * f.quantite for f in factures_vente)
        ca_text = f"Le chiffre d'affaire : {ca} DT"
        ca_style = getSampleStyleSheet()['Heading3']
        ca_paragraph = Paragraph(ca_text, ca_style)
        elements.append(ca_paragraph)
        def group_and_calculate_totals(factures):
            grouped = {}
            for facture in factures:
                facture_date = parse_date(facture.date)
                month = facture_date.strftime('%Y-%m')
                if month not in grouped:
                    grouped[month] = []
                grouped[month].append(facture)
            return grouped

        def parse_date(date_str):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y %H:%M:%S'):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    pass
            raise ValueError(f"No valid date format found for {date_str}")

        def add_totals_to_table(data, factures):
            grouped = group_and_calculate_totals(factures)
            for month, factures in grouped.items():
                for facture in factures:
                    facture_date = parse_date(facture.date)
                    data.append([
                        facture_date.strftime('%d-%m-%Y'), 
                        facture.numero_facture, 
                        facture.nom_client if facture.catéogorie == 'Vente' else facture.nom_fournisseur,
                        facture.libelle, 
                        Decimal(str(facture.prix_unitaire)), 
                        facture.quantite, 
                        Decimal(str(facture.total_ttc))
                    ])
                total_ttc = sum(Decimal(str(f.total_ttc)) for f in factures)
                data.append([
                    'Total ' + calendar.month_name[int(month.split('-')[1])], '', '', '', '','', total_ttc
                ])

        title_achat_text = "Factures d'Achat"
        title_achat_style = getSampleStyleSheet()['Heading1']
        title_achat = Paragraph(title_achat_text, title_achat_style)
        
        data_achat = [['Date', 'Num Facture', 'Fournisseur', 'Libelle', 'Prix Unitaire', 'Quantite', 'Total TTC']]
        add_totals_to_table(data_achat, factures_achat)

        style_title = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table_achat = Table(data_achat)
        table_achat.setStyle(style_title)
        
        elements.append(title_achat)
        elements.append(table_achat)
        elements.append(Spacer(1, 20))

        title_vente_text = "Factures de Vente"
        title_vente_style = getSampleStyleSheet()['Heading1']
        title_vente = Paragraph(title_vente_text, title_vente_style)

        data_vente = [['Date', 'Num Facture', 'Client', 'Libelle', 'Prix Unitaire', 'Quantite', 'Total TTC']]
        add_totals_to_table(data_vente, factures_vente)

        table_vente = Table(data_vente)
        table_vente.setStyle(style_title)

        elements.append(title_vente)
        elements.append(table_vente)

        pdf.build(elements)
        
        return response
    else:
        return HttpResponse("Dataimport ID is missing.", status=400)
from django.db.models.functions import TruncMonth, ExtractYear
def dashboard1(request):
    dataimport_id = request.GET.get('dataimport_id')  # Récupérer l'ID depuis la requête GET
    if dataimport_id:
        try:
            dataimport_instance = dataimport.objects.get(pk=dataimport_id)

            # Calcul des statistiques
            nombre_ventes = fait_vente.objects.count()
            nombre_achats = fait_achat.objects.count()
            nombre_factures = nombre_ventes  + nombre_achats

            nombre_fournisseurs = Dim_Fournisseur.objects.distinct().count()
            nombre_clients = Dim_Client.objects.distinct().count()

            total_revenue = fait_vente.objects.aggregate(Sum('total_ttc'))['total_ttc__sum'] or 0
            # Nombre d'achats par mois
            achats_par_mois = (
                fait_achat.objects
                .annotate(month=TruncMonth('id_temps__id_Tempss'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )

            # Nombre de ventes par mois
            ventes_par_mois = (
                fait_vente.objects
                .annotate(month=TruncMonth('id_temps__id_Tempss'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
            # Préparer les données pour Chart.js
            labels = [achat['month'].strftime('%Y-%m') for achat in achats_par_mois]
            achats_data = [achat['count'] for achat in achats_par_mois]
            ventes_data = [vente['count'] for vente in ventes_par_mois]
            # Obtenez le chiffre d'affaires par mois
            chiffre_affaires_par_mois = (
                fait_vente.objects
                .annotate(mois=ExtractMonth('id_temps__id_Tempss'), annee=ExtractYear('id_temps__id_Tempss'))
                .values('mois', 'annee')
                .annotate(ca=Sum('ca'))
                .order_by('annee', 'mois')
            )
            # Préparez les données pour le graphique
            mois_labels = []
            ca_values = []

            for item in chiffre_affaires_par_mois:
                mois_labels.append(datetime(item['annee'], item['mois'], 1).strftime('%B %Y'))
                ca_values.append(float(item['ca']))
            context = {
                'dataimport_instance': dataimport_instance,
                'nombre_ventes': nombre_ventes,
                'nombre_total_factures_achat': nombre_achats,
                'nombre_factures': nombre_factures,
                'nombre_fournisseurs': nombre_fournisseurs,
                'nombre_clients': nombre_clients,
                'total_revenue': total_revenue,
                'labels': labels,
                'achat_par_mois': achats_data,
                'ventes_par_mois': ventes_data,
                'mois_labels': mois_labels,
                'chiffre_affaires_liste': ca_values,
            }
            return render(request, 'pfe/dashboard1.html', context)
        except dataimport.DoesNotExist:
            return HttpResponse("Dataimport avec cet ID non trouvé.", status=404)
    
    return render(request, 'test.html') 
   
def dashboard1(request):
    dataimport_id = request.GET.get('dataimport_id')  # Récupérer l'ID depuis la requête GET
    if dataimport_id:
        try:
            dataimport_instance = dataimport.objects.get(pk=dataimport_id)
            
            # Filtrer les faits par dataimport_instance
            ventes = fait_vente.objects.filter(client_ent=dataimport_instance)
            achats = fait_achat.objects.filter(client_ent=dataimport_instance)

            # Calculer le nombre total de ventes et d'achats
            nombre_ventes = ventes.count()
            nombre_achats = achats.count()
            
            # Calculer le nombre de clients et de fournisseurs
            nombre_clients = Dim_Client.objects.filter(fait_vente__client_ent=dataimport_instance).distinct().count()
            nombre_fournisseurs = Dim_Fournisseur.objects.filter(fait_achat__client_ent=dataimport_instance).distinct().count()
            
            # Calculer le revenu total
            total_revenue_ventes = ventes.aggregate(total=Sum('total_ttc'))['total'] or Decimal('0.00')
            total_revenue_achats = achats.aggregate(total=Sum('total_ttc'))['total'] or Decimal('0.00')
            total_revenue = total_revenue_ventes - total_revenue_achats
            
            # Comptage du nombre de fois que chaque produit apparaît dans les ventes
            produits_counter = ventes.values('id_produit__libelle').annotate(total=Count('id_produit')).order_by()
            total_produits = sum(item['total'] for item in produits_counter)
            resultats_de_revenue_par_produit = [(item['id_produit__libelle'], (item['total'] / total_produits) * 100) for item in produits_counter]
            
            # Création des étiquettes pour les mois de l'année suivante
            labels_mois_suivant = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            
            # Ventes et achats par mois
            ventes_par_mois = defaultdict(int)
            achats_par_mois = defaultdict(int)
            for vente in ventes:
                mois = vente.id_temps.mois
                ventes_par_mois[mois] += 1
            for achat in achats:
                mois = achat.id_temps.mois
                achats_par_mois[mois] += 1
            ventes_par_mois_list = [ventes_par_mois.get(str(mois).zfill(2), 0) for mois in range(1, 13)]
            achats_par_mois_list = [achats_par_mois.get(str(mois).zfill(2), 0) for mois in range(1, 13)]
            ventes_json = json.dumps(ventes_par_mois_list)
            achats_json = json.dumps(achats_par_mois_list)
            
            # Calcul du CA par mois
            chiffre_affaires_par_mois = ventes.values('id_temps__mois').annotate(chiffre_affaire=Sum('CA')).order_by('id_temps__mois')
            chiffre_affaires_liste = [chiffre_affaires_par_mois.get(str(mois).zfill(2), Decimal('0.00')) for mois in range(1, 13)]
            
            # Calcul du CA prévisionnel
            facteur_croissance = Decimal('1.20')
            chiffre_affaires_previsionnel_annee_suivante = [chiffre_affaire * facteur_croissance for chiffre_affaire in chiffre_affaires_liste]
            
            # CA par produit par mois
            chiffre_affaires_par_produit_par_mois = defaultdict(lambda: defaultdict(Decimal))
            for vente in ventes:
                mois = vente.id_temps.mois
                chiffre_affaire_produit = vente.total_ttc
                produit_libelle = vente.id_produit.libelle
                chiffre_affaires_par_produit_par_mois[mois][produit_libelle] += chiffre_affaire_produit

            # Produit par vente
            produits_ttc = ventes.values('id_produit__libelle').annotate(total_ttc=Sum('total_ttc')).order_by()
            produits_ttc_list = [(item['id_produit__libelle'], item['total_ttc']) for item in produits_ttc]
            
            # Produit par achat
            produits_ttc_achat = achats.values('id_produit__libelle').annotate(total_ttc=Sum('total_ttc')).order_by()
            produits_ttc_achat_list = [(item['id_produit__libelle'], item['total_ttc']) for item in produits_ttc_achat]
            
            context = {
                'produits_ttc1': produits_ttc_achat_list,
                'produits_ttc': produits_ttc_list,
                'chiffre_affaire_total': total_revenue,
                'dataimport_instance': dataimport_instance,
                'nombre_factures': nombre_ventes + nombre_achats,
                'nom_client': dataimport_instance.client.clientName,
                'nombre_fournisseurs': nombre_fournisseurs,
                'nombre_clients': nombre_clients,
                'nombre_achats': nombre_achats,
                'nombre_ventes': nombre_ventes,
                'ventes_par_mois': ventes_json,
                'achats_par_mois': achats_json,
                'total_revenue': total_revenue,
                'resultats_de_revenue_par_produit': resultats_de_revenue_par_produit,
                'labels_mois_suivant': labels_mois_suivant,
                'dataimport_id': dataimport_id,
                'chiffre_affaires_liste': chiffre_affaires_liste,
                'chiffre_affaire_previsionnel': chiffre_affaires_previsionnel_annee_suivante,
            }
            return render(request, 'pfe/dashboard1.html', context)
        except dataimport.DoesNotExist:
            return HttpResponse("Dataimport avec cet ID non trouvé.", status=404)
    else:
        return HttpResponse("ID de dataimport vide.", status=400)


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
    