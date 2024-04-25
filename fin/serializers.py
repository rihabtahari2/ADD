from rest_framework.serializers import ModelSerializer
from fin.models import client
class ClientSerializer(ModelSerializer):
    class Meta:
        model = client
        fields = ('clientId', 'clientName', 'clientAdresse')

