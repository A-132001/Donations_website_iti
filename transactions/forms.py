from django import forms
from .models import Transaction
from campaigns.models import Campaign

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['donor_name', 'donor_phone_number', 'donation_date', 'to_campaign', 'amount']
        widgets = {
            'donation_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'donor_name': 'Donor Name',
            'donor_phone_number': 'Phone Number',
            'donation_date': 'Donation Date',
            'to_campaign': 'Campaign',
            'amount': 'Donation Amount',
        }

    def clean_amount(self):
        """
        Clean the donation amount to ensure it's positive.
        """
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Donation amount must be greater than 0.")
        return amount
