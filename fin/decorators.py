from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from functools import wraps

def expert_required(view_func):
    @wraps(view_func)  # Assure la préservation des métadonnées de la vue décorée
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name='Experts').exists():  # Vérifie si l'utilisateur appartient au groupe "Expert"
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied  # Lève une exception si l'utilisateur n'a pas la permission
    return wrapper
