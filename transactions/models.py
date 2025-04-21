from django.db import models
from campaigns.models import Campaign

class Transaction(models.Model):
    donor_name = models.CharField(max_length=100, default="benefactor-unknown")
    donor_phone_number = models.CharField(max_length=20, blank=True)

    donation_date = models.DateField()
    to_campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        campaign = self.to_campaign
        campaign.current_amount += self.amount
        if campaign.current_amount >= campaign.target_amount:
            campaign.status = 'completed'
        campaign.save()
    def __str__(self):
        return f"Donation by {self.donor_name} of ${self.amount} to {self.to_campaign.title} on {self.donation_date}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-donation_date']
        db_table = 'transactions'