from django.db import models
from shared_models.common.base import BaseModel

class CustomerCryptoWallet(BaseModel):
    id = models.AutoField(primary_key=True, editable=False)
    customer_id = models.IntegerField(db_index=True)
    address = models.CharField(max_length=255)
    network = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    comment = models.TextField(blank=True, null=True, help_text='Additional notes about this crypto wallet')

    class Meta:
        app_label = 'shared_customer_crypto_wallet'
        db_table = 'shared_customer_crypto_wallets'
        verbose_name = 'Customer Crypto Wallet'
        verbose_name_plural = 'Customer Crypto Wallets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['address', 'network']),
            models.Index(fields=['token']),
        ]
        permissions = [
            ('view_customer_crypto_wallet', 'Can view customer crypto wallet'),
            ('delete_customer_crypto_wallet', 'Can delete customer crypto wallet'),
            ('change_customer_crypto_wallet', 'Can change customer crypto wallet'),
            ('add_customer_crypto_wallet', 'Can add customer crypto wallet')
        ]

    def __str__(self):
        return f"Customer Crypto Wallet {self.address} ({self.network}/{self.token})"
