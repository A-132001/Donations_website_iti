from django.urls import path
from .views import TransactionListView, TransactionDetailView, TransactionCreateView, TransactionDeleteView, TransactionUpdateView

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('transaction/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('transaction/new/', TransactionCreateView.as_view(), name='transaction-create'),
    path('transaction/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction-delete'),
    path('transaction/<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction-update'),
]
