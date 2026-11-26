from django.shortcuts import render
from django.db import models

# Create your views here.


from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.models import Account
from .models import Transaction
from .serializers import DepositSerializer,WithdrawalSerializer,TransactionSerializer,TransferSerializer
from rest_framework.pagination import PageNumberPagination

class DepositView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = DepositSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            account = get_object_or_404(
                Account.objects.select_for_update(),
                id=serializer.validated_data['account_id'],
                user=request.user
            )

            amount = serializer.validated_data['amount']

            account.balance += amount
            account.save(update_fields=['balance', 'updated_at'])

            transaction_record = Transaction.objects.create(
                user=request.user,
                destination_account=account,
                transaction_type='DEPOSIT',
                amount=amount,
                description=serializer.validated_data.get('description', ''),
                status='SUCCESS'
            )

        return Response(
            {
                "message": "Deposit successful",
                "transaction_id": str(transaction_record.id),
                "new_balance": str(account.balance)
            },
            status=status.HTTP_201_CREATED
        )




class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = WithdrawalSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            try:
                account = Account.objects.select_for_update().get(
                    id=serializer.validated_data['account_id'],
                    user=request.user
                )
            except Account.DoesNotExist:
                return Response(
                    {"error": "Account not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            amount = serializer.validated_data['amount']

            if account.balance < amount:
                return Response(
                    {"error": "Insufficient balance"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            account.balance -= amount

            account.save(
                update_fields=['balance', 'updated_at']
            )

            transaction_record = Transaction.objects.create(
                user=request.user,
                source_account=account,
                transaction_type='WITHDRAWAL',
                amount=amount,
                description=serializer.validated_data.get(
                    'description', ''
                ),
                status='SUCCESS'
            )

        return Response({
            "message": "Withdrawal successful",
            "transaction_id": str(transaction_record.id),
            "new_balance": str(account.balance)
        }, status=status.HTTP_201_CREATED)






from rest_framework.pagination import PageNumberPagination

class TransactionHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        transactions = Transaction.objects.filter(
            user=request.user
        ).select_related(
            'source_account',
            'destination_account'
        ).order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(
            transactions,
            request,
            view=self
        )

        serializer = TransactionSerializer(
            result_page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )




class AccountTransactionHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, account_id):

        try:
            account = Account.objects.get(
                id=account_id,
                user=request.user
            )
        except Account.DoesNotExist:
            return Response(
                {"error": "Account not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        transactions = Transaction.objects.filter(
            user=request.user
        ).filter(
            models.Q(source_account=account) |
            models.Q(destination_account=account)
        ).select_related(
            'source_account',
            'destination_account'
        ).order_by('-created_at')

        serializer = TransactionSerializer(
            transactions,
            many=True
        )

        return Response(serializer.data)



class TransferView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = TransferSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        source_id = serializer.validated_data['source_account_id']
        destination_id = serializer.validated_data['destination_account_id']
        amount = serializer.validated_data['amount']

        with transaction.atomic():

            accounts = list(
                Account.objects.select_for_update()
                .filter(
                    id__in=[source_id, destination_id],
                    user=request.user
                )
                .order_by('id')
            )

            if len(accounts) != 2:
                return Response(
                    {"error": "Source or destination account not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            account_map = {account.id: account for account in accounts}

            source_account = account_map[source_id]
            destination_account = account_map[destination_id]

            if source_account.balance < amount:
                return Response(
                    {"error": "Insufficient balance"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            source_account.balance -= amount
            destination_account.balance += amount

            source_account.save(
                update_fields=['balance', 'updated_at']
            )

            destination_account.save(
                update_fields=['balance', 'updated_at']
            )

            transaction_record = Transaction.objects.create(
                user=request.user,
                source_account=source_account,
                destination_account=destination_account,
                transaction_type='TRANSFER',
                amount=amount,
                description=serializer.validated_data.get('description', ''),
                status='SUCCESS'
            )

        return Response(
            {
                "message": "Transfer successful",
                "transaction_id": str(transaction_record.id),
                "source_account_balance": str(source_account.balance),
                "destination_account_balance": str(destination_account.balance)
            },
            status=status.HTTP_201_CREATED
        )
