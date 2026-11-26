from django.urls import path
from .views import DepositView,WithdrawalView,TransactionHistoryView,AccountTransactionHistoryView

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawalView.as_view(), name='withdraw'),
    path('history/', TransactionHistoryView.as_view(), name='transaction-history'),
    path(
    'accounts/<uuid:account_id>/history/',
    AccountTransactionHistoryView.as_view(),
    name='account-transaction-history'
),
]
