from django.urls import path
from . import views

urlpatterns = [
    #path('',views.login, name='login'),
    path('home/',views.home, name='home'),
    path('base/',views.base, name='base'),
    path('register/',views.register, name='register'),
    path('',views.singin, name='singin'),
    path('logout/',views.logoutUser, name='logout'),
    path('navbar1/',views.navbar1, name='navbar'),

    path('client/',views.list_client, name='client'),
    path('add_client/',views.add_client, name='add_client'),
    path('update_client/<str:pk>',views.update_client, name='update_client'),

    path('delete_client/<str:pk>', views.delete_client, name='delete_client'),

    path('assistant/',views.list_assistant, name='assistant'),
    path('add_assistant/',views.add_assistant, name='add_assistant'),
    path('update_assistant/<str:pk>/', views.update_assistant, name='update_assistant'),
    path('client_assistant/<int:pk>/',views.client_assistant, name='client_assistant'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    path('HomePage/',views.home_page, name='Home'),
    path('donne/<int:fichier_id>/',views.donn, name='données'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('import_data/<int:fichier_id>/',views.import_data, name='import_data'),
    path('test/',views.test, name='test'),
    path('test/import_file/',views.import_file, name='import_file'),
    path('save_data/',views.save_data, name='save_data'),

    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/csv/', views.export_csv, name='export_csv'),

    path('ex/',views.expl, name='l'),
    path('exx/',views.expl1, name='expl'),

    path('create_user/', views.create_user, name='create_user'),
    path('users/', views.user_list, name='user_list'),
    
]
   