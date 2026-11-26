from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Account
from .serializers import AccountSerializer


class AccountCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AccountSerializer(data=request.data)

        if serializer.is_valid():

            account = serializer.save(user=request.user)

            return Response(
                AccountSerializer(account).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AccountListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        accounts = Account.objects.filter(
            user=request.user
        )

        serializer = AccountSerializer(
            accounts,
            many=True
        )

        return Response(serializer.data)



class AccountDetailView(APIView):

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

        serializer = AccountSerializer(account)

        return Response(serializer.data)
class AccountDetailView(APIView):

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

        serializer = AccountSerializer(account)

        return Response(serializer.data)
