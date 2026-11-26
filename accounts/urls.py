from django.urls import path
from .views import AccountCreateView,AccountListView,AccountDetailView

urlpatterns = [
    path('', AccountCreateView.as_view(), name='account-create'),
    path('list/', AccountListView.as_view(), name='account-list'),
    path('<uuid:account_id>/', AccountDetailView.as_view(), name='account-detail'),
]
