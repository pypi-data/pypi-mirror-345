from django.db import models
from ..common.base import BaseModel
from ..services.group_resolver import MT5GroupResolverService

class Account(BaseModel):
    """
    Trading account model
    """
    id = models.AutoField(primary_key=True, editable=False)
    
    # Relations
    server = models.ForeignKey('system_settings.TradingPlatformServer',
                             on_delete=models.PROTECT,
                             related_name='accounts')
    account_type = models.ForeignKey('system_settings.AccountType',
                                   on_delete=models.PROTECT,
                                   related_name='accounts')
    customer = models.ForeignKey('customers.Customer',
                               on_delete=models.CASCADE,
                               related_name='accounts')
    
    # Account Details
    login = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    is_trading_enabled = models.BooleanField(default=True)
    
    # Group Configuration
    is_swap_free = models.BooleanField(
        default=False,
        help_text="Whether this account uses Islamic (swap-free) groups"
    )
    has_bonus = models.BooleanField(
        default=False,
        help_text="Whether this account has bonus applied"
    )
    has_markup = models.BooleanField(
        default=False,
        help_text="Whether this account has markup applied"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
    )

    class Meta:
        app_label = 'accounts'
        db_table = 'accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        unique_together = [['login', 'server']]
        indexes = [
            models.Index(fields=['login', 'server']),
            models.Index(fields=['customer']),
            models.Index(fields=['account_type']),
        ]
        permissions = [
            ("view_own_account", "Can view own customer accounts"),
            ("view_team_account", "Can view team's customer accounts"),
            ("view_all_account", "Can view all customer accounts"),
            ("change_account_group", "Can change account group"),
        ]

    def __str__(self):
        return f"Account {self.login} ({self.customer.email})"
        
    @property
    def current_group(self):
        """Get the current MT5 group path for this account"""
        return MT5GroupResolverService.resolve_group(self) 