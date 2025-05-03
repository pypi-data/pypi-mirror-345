from django.db import models
from shared_models.common.base import BaseModel

class CustomerUPI(BaseModel):
    id = models.AutoField(primary_key=True, editable=False)
    customer_id = models.IntegerField(db_index=True)
    upi_id = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    comment = models.TextField(blank=True, null=True, help_text='Additional notes about this UPI ID')

    class Meta:
        app_label = 'shared_customer_upi'
        db_table = 'shared_customer_upi'
        verbose_name = 'Customer UPI'
        verbose_name_plural = 'Customer UPIs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['upi_id']),
        ]
        permissions = [
            ('view_customer_upi', 'Can view customer UPI'),
            ('delete_customer_upi', 'Can delete customer UPI'),
            ('change_customer_upi', 'Can change customer UPI'),
            ('add_customer_upi', 'Can add customer UPI')
        ]

    def __str__(self):
        return f"Customer UPI {self.upi_id} (Customer ID: {self.customer_id})"
