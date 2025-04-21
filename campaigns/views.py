from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Campaign
from .forms import CampaignForm
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q



# class BaseCampaignView(View):
class BaseCampaignView(LoginRequiredMixin,View):
    template_name = None
    redirect_url = None
    def get_redirect_url(self):
        if self.redirect_url:
            return reverse_lazy(self.redirect_url)
        return reverse_lazy('campaign-list')
    
    def get_context_data(self, **kwargs):
        context = {}
        context.update(kwargs)
        return context


class CampaignListView(BaseCampaignView):
    template_name = 'campaigns/campaign_list.html'
    def get(self, request, *args, **kwargs):
        show_mine = request.GET.get('show_mine') == 'true'
        campaigns = Campaign.objects.filter(owner=request.user) if show_mine else Campaign.objects.all()
        
        search_query = request.GET.get('q')
        status_filter = request.GET.get('status')
        
        if search_query:
            campaigns = campaigns.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        if status_filter and status_filter != 'all':
            campaigns = campaigns.filter(status=status_filter)
            
        campaigns = campaigns.order_by('-created_at')
        
        context = self.get_context_data(
            campaigns=campaigns,
            search_query=search_query,
            status_choices=Campaign.STATUS_CHOICES,
            current_status=status_filter if status_filter else 'all',
            show_mine=show_mine
        )
        return render(request, self.template_name, context)

class CampaignDetailView(BaseCampaignView):
    template_name = 'campaigns/campaign_detail.html'    
    def get(self,req,pk,*arg,**kwargs):
        campaign = get_object_or_404(Campaign, pk=pk)
        context = self.get_context_data(campaign=campaign)
        return render(req, self.template_name, context)

class CampaignCreateView(BaseCampaignView):
    template_name = 'campaigns/campaign_form.html'
    redirect_url = 'campaigns:campaign_list'
    
    def get(self, req, *args, **kwargs):
        context = self.get_context_data(form=CampaignForm())
        return render(req, self.template_name, context) 
    
    def post(self, req, *args, **kwargs):
        form = CampaignForm(req.POST, req.FILES)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.owner = req.user
            campaign.current_amount = 0.00
            campaign.save()
            messages.success(req, 'Campaign created successfully!')
            return redirect(self.get_redirect_url())
        context = self.get_context_data(form=form)
        return render(req, self.template_name, context)
    

class CampaignUpdateView(BaseCampaignView):
    template_name = 'campaigns/campaign_form.html'
    redirect_url = 'campaigns:campaign_list'
    
    def get(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=pk)
        if campaign.owner != request.user:
            raise PermissionDenied
        form = CampaignForm(instance=campaign)
        context = self.get_context_data(form=form, object=campaign)
        return render(request, self.template_name, context)
    
    def post(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=pk)
        if campaign.owner != request.user:
            raise PermissionDenied
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign updated successfully!')
            return redirect(self.get_redirect_url())
        context = self.get_context_data(form=form, object=campaign)
        return render(request, self.template_name, context)


class CampaignDeleteView(BaseCampaignView):
    template_name = 'campaigns/campaign_delete.html'
    redirect_url = 'campaigns:campaign_list'
    
    def get(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=pk)
        if campaign.owner != request.user:
            raise PermissionDenied
        context = self.get_context_data(object=campaign)
        return render(request, self.template_name, context)
    
    def post(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=pk)
        if campaign.owner != request.user:
            raise PermissionDenied
        campaign.delete()
        messages.success(request, 'Campaign deleted successfully!')
        return redirect(self.get_redirect_url())

def home(request):
    latest_campaigns =  base_queryset = Campaign.objects.filter(status='ongoing').order_by('-created_at')[:5]
    top_donated_campaigns =  base_queryset = Campaign.objects.filter(status='ongoing').order_by('-current_amount')[:5]
    completed_campaigns =  base_queryset = Campaign.objects.filter(status='completed').order_by('-created_at')[:5]
    
    context = {
        'latest_campaigns': latest_campaigns,
        'top_donated_campaigns': top_donated_campaigns,
        'completed_campaigns': completed_campaigns,
    }
    return render(request, '../templates/homepage.html', context)


    
# class CampaignListView(ListView):
#     model = Campaign
#     template_name = 'campaigns/campaign_list.html'
#     context_object_name = 'campaigns'

# class CampaignDetailView(DetailView):
#     model = Campaign
#     template_name = 'campaigns/campaign_detail.html'
#     context_object_name = 'campaigns'


# class CampaignCreateView(LoginRequiredMixin, CreateView):
#     model = Campaign
#     form_class = CampaignForm
#     template_name = 'campaigns/campaign_form.html'
#     success_url = reverse_lazy('campaigns:campaign_list')

#     def form_valid(self, form):
#         form.instance.owner = self.req.user  
#         return super().form_valid(form)
