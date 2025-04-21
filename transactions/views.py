from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from .models import Transaction
from .forms import TransactionForm

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10  # Paginate to limit the number of records per page

    def get_queryset(self):
        queryset = super().get_queryset()

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(donation_date__range=[start_date, end_date])
        for q in queryset:
            print(q)
        return queryset

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'transaction_detail.html'
    context_object_name = 'transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = self.object

      
        total_donations = Transaction.objects.filter(to_campaign=transaction.to_campaign).aggregate(total=Sum('amount'))
        context['total_donations'] = total_donations['total'] or 0
        return context

class TransactionCreateView(CreateView):
    model = Transaction
    template_name = 'transaction_form.html'
    form_class = TransactionForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Transaction created successfully!')

        return redirect('transaction-list')

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your form. Please check the details and try again.')
        for field, errors in form.errors.items():
            print(f"Field: {field}, Errors: {errors}")

        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('transaction-list')

class TransactionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Transaction
    template_name = 'transaction_confirm_delete.html'
    context_object_name = 'transaction'
    success_url = reverse_lazy('transaction-list')

    def form_valid(self, form):
        messages.success(self.request, 'Transaction deleted successfully!')
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_staff
    
class TransactionUpdateView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = Transaction
    template_name = 'transaction_form.html'  
    form_class = TransactionForm  
    context_object_name = 'transaction' 
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Transaction updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('transaction-list')

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your form. Please check the details and try again.')
        for field, errors in form.errors.items():
            print(f"Field: {field}, Errors: {errors}")
        return super().form_invalid(form)
    
    def test_func(self):
        return self.request.user.is_staff
    

