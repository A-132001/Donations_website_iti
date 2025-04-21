from django.urls import path
from .views import *

app_name = 'campaigns'

urlpatterns = [
    path('', CampaignListView.as_view(), name='campaign_list'),
    path('detail/<int:pk>', CampaignDetailView.as_view(), name='detail'),
    path('create/', CampaignCreateView.as_view(), name='create'),
    path('update/<int:pk>', CampaignUpdateView.as_view(), name='update'),
    path('delete/<int:pk>', CampaignDeleteView.as_view(), name='delete'),
]
