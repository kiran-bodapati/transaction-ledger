from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = [
            'id',
            'account_number',
            'name',
            'account_type',
            'balance',
            'currency',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'account_number',
            'balance',
            'created_at',
            'updated_at',
        ]
