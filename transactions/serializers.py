from rest_framework import serializers
from .models import Transaction


class DepositSerializer(serializers.ModelSerializer):

    account_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Transaction
        fields = [
            'account_id',
            'amount',
            'description',
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Deposit amount must be greater than zero."
            )

        return value




class WithdrawalSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Withdrawal amount must be greater than zero."
            )
        return value



from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):

    source_account_name = serializers.CharField(
        source='source_account.name',
        read_only=True
    )

    destination_account_name = serializers.CharField(
        source='destination_account.name',
        read_only=True
    )

    class Meta:
        model = Transaction

        fields = [
            'id',
            'transaction_type',
            'source_account',
            'source_account_name',
            'destination_account',
            'destination_account_name',
            'amount',
            'description',
            'status',
            'created_at'
        ]
