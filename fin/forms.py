from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CreateUserform (UserCreationForm):
    clients = forms.ModelMultipleChoiceField(queryset=client.objects.all(), required=False)
    class Meta:
        model=User
        fields=('username','email','password1','password2','first_name', 'last_name')

class ClientForm(forms.ModelForm):
    class Meta:
        model = client
        fields = ('clientName','clientAdresse','clientActivity','contact')

class FichiersForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=client.objects.all(), 
                                    empty_label=None, 
                                    label='Choisir un client', 
                                    to_field_name='clientName',
                                    widget=forms.Select(attrs={'class': 'utilisateur-input'}))
    nom = forms.CharField(label='Nom d\'espace de travaille', initial='Espace de travaille')
    description = forms.CharField(label='Description', widget=forms.Textarea(attrs={'rows': 3}))
    class Meta:
        model = dataimport
        fields = ('nom', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Vous pouvez retirer l'ordre ici, car le champ 'clientName' sera utilisé pour trier automatiquement
        self.fields['client'].queryset = client.objects.all()





class UploadFileForm(forms.Form):
   my_file = forms.FileField(label='Select a file')
