from django.core.cache import cache
import logging

logger = logging.getLogger('commission_cache')

class CommissionCacheService:
    """Service for caching commission-related data using Django's cache framework"""
    
    # Cache key patterns (use consistent patterns across projects)
    RULE_CACHE_KEY = "commission_rule:{agreement_id}:{symbol}:{commission_type}"
    AGREEMENT_CACHE_KEY = "ib_agreement:{customer_id}"
    HIERARCHY_CACHE_KEY = "ib_hierarchy:{customer_id}"
    CLIENT_MAPPING_CACHE_KEY = "client_mapping:{mt5_login}:{customer_id}"
    ACCOUNT_CACHE_KEY = "account:{mt5_login}"
    
    # Cache expiration times (in seconds)
    RULE_CACHE_EXPIRY = 3600 * 24  # 24 hours
    AGREEMENT_CACHE_EXPIRY = 3600 * 24  # 24 hours
    HIERARCHY_CACHE_EXPIRY = 3600 * 24  # 24 hours
    CLIENT_MAPPING_CACHE_EXPIRY = 3600 * 24  # 24 hours
    ACCOUNT_CACHE_EXPIRY = 3600 * 24  # 24 hours
    
    # Flag to enable/disable cache
    CACHE_ENABLED = True
    
    @classmethod
    def get_account(cls, mt5_login):
        """
        Get account from cache or database
        
        Args:
            mt5_login: The MT5 login
            
        Returns:
            Account object or None
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching account from database")
            return cls._get_account_from_db(mt5_login)
            
        from shared_models.accounts.models import Account
        
        cache_key = cls.ACCOUNT_CACHE_KEY.format(mt5_login=mt5_login)
        
        logger.info(f"Looking for account cache key: {cache_key}")
        
        # Try to get from cache first
        account = cache.get(cache_key)
        if account:
            logger.info(f"Account cache hit for {cache_key}")
            return account
        
        logger.info(f"Account cache miss for {cache_key}")
        
        # If not in cache, get from database
        account = cls._get_account_from_db(mt5_login)
        
        if account:
            # Store in cache for future use
            logger.info(f"Storing account in cache: {cache_key}")
            cache.set(cache_key, account, cls.ACCOUNT_CACHE_EXPIRY)
        
        return account
    
    @classmethod
    def _get_account_from_db(cls, mt5_login):
        """Get account directly from database"""
        from shared_models.accounts.models import Account
        
        logger.info(f"Fetching account from DB for mt5_login={mt5_login}")
        
        account = Account.objects.filter(login=mt5_login, is_active=True).first()
        
        logger.info(f"Found account in database: {account is not None}")
        return account
    
    @classmethod
    def invalidate_account_cache(cls, mt5_login):
        """
        Invalidate account cache
        
        Args:
            mt5_login: The MT5 login
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping account invalidation")
            return
            
        cache_key = cls.ACCOUNT_CACHE_KEY.format(mt5_login=mt5_login)
        logger.info(f"Invalidating account cache key: {cache_key}")
        cache.delete(cache_key)
    
    @classmethod
    def get_commission_rules(cls, agreement_id, symbol, commission_type):
        """
        Get commission rules from cache or database
        
        Args:
            agreement_id: The agreement ID
            symbol: The trading symbol
            commission_type: The commission type (COMMISSION or REBATE)
            
        Returns:
            List of commission rules
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching from database")
            return cls._get_commission_rules_from_db(agreement_id, symbol, commission_type)
            
        from shared_models.ib_commission.models import IBCommissionRule
        from django.db import models
        
        cache_key = cls.RULE_CACHE_KEY.format(
            agreement_id=agreement_id,
            symbol=symbol if symbol is not None else "none",
            commission_type=commission_type
        )
        
        logger.info(f"Looking for cache key: {cache_key}")
        
        # Try to get from cache first
        rules = cache.get(cache_key)
        if rules:
            logger.info(f"Cache hit for {cache_key}")
            return rules
        
        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, get from database
        rules = cls._get_commission_rules_from_db(agreement_id, symbol, commission_type)
        
        # Store in cache for future use
        logger.info(f"Storing in cache: {cache_key}")
        cache.set(cache_key, rules, cls.RULE_CACHE_EXPIRY)
        
        return rules
    
    @classmethod
    def _get_commission_rules_from_db(cls, agreement_id, symbol, commission_type):
        """Get commission rules directly from database"""
        from shared_models.ib_commission.models import IBCommissionRule
        from django.db import models
        
        logger.info(f"Fetching rules from DB for agreement_id={agreement_id}, symbol={symbol}, commission_type={commission_type}")
        
        rules = list(IBCommissionRule.objects.filter(
            agreement_id=agreement_id,
            commission_type=commission_type
        ).filter(
            models.Q(symbol__iexact=symbol) | models.Q(symbol='*') | models.Q(symbol__isnull=True)
        ).order_by('priority'))
        
        logger.info(f"Found {len(rules)} rules in database")
        return rules
    
    @classmethod
    def get_ib_agreements(cls, customer_id):
        """
        Get IB agreements from cache or database
        
        Args:
            customer_id: The customer ID
            
        Returns:
            List of agreement memberships
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching from database")
            return cls._get_ib_agreements_from_db(customer_id)
            
        from shared_models.ib_commission.models import IBAgreementMember
        
        cache_key = cls.AGREEMENT_CACHE_KEY.format(customer_id=customer_id)
        
        logger.info(f"Looking for cache key: {cache_key}")
        
        # Try to get from cache first
        agreements = cache.get(cache_key)
        if agreements:
            logger.info(f"Cache hit for {cache_key}")
            return agreements
        
        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, get from database
        agreements = cls._get_ib_agreements_from_db(customer_id)
        
        # Store in cache for future use
        logger.info(f"Storing in cache: {cache_key}")
        cache.set(cache_key, agreements, cls.AGREEMENT_CACHE_EXPIRY)
        
        return agreements
    
    @classmethod
    def _get_ib_agreements_from_db(cls, customer_id):
        """Get IB agreements directly from database"""
        from shared_models.ib_commission.models import IBAgreementMember
        
        logger.info(f"Fetching agreements from DB for customer_id={customer_id}")
        
        agreements = list(IBAgreementMember.objects.filter(
            customer_id=customer_id,
            is_active=True
        ).select_related('agreement'))
        
        logger.info(f"Found {len(agreements)} agreements in database")
        return agreements
    
    @classmethod
    def get_ib_hierarchy(cls, customer_id):
        """
        Get IB hierarchy from cache or database
        
        Args:
            customer_id: The customer ID
            
        Returns:
            IBHierarchy object
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching from database")
            return cls._get_ib_hierarchy_from_db(customer_id)
            
        from shared_models.ib_commission.models import IBHierarchy
        
        cache_key = cls.HIERARCHY_CACHE_KEY.format(customer_id=customer_id)
        
        logger.info(f"Looking for cache key: {cache_key}")
        
        # Try to get from cache first
        hierarchy = cache.get(cache_key)
        if hierarchy:
            logger.info(f"Cache hit for {cache_key}")
            return hierarchy
        
        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, get from database
        hierarchy = cls._get_ib_hierarchy_from_db(customer_id)
        
        if hierarchy:
            # Store in cache for future use
            logger.info(f"Storing in cache: {cache_key}")
            cache.set(cache_key, hierarchy, cls.HIERARCHY_CACHE_EXPIRY)
        
        return hierarchy
    
    @classmethod
    def _get_ib_hierarchy_from_db(cls, customer_id):
        """Get IB hierarchy directly from database"""
        from shared_models.ib_commission.models import IBHierarchy
        
        logger.info(f"Fetching hierarchy from DB for customer_id={customer_id}")
        
        hierarchy = IBHierarchy.objects.filter(
            customer_id=customer_id,
            is_active=True
        ).first()
        
        logger.info(f"Found hierarchy in database: {hierarchy is not None}")
        return hierarchy
    
    @classmethod
    def get_client_mapping(cls, mt5_login, customer_id):
        """
        Get client mapping from cache or database
        
        Args:
            mt5_login: The MT5 login
            customer_id: The customer ID
            
        Returns:
            ClientIBMapping object
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching from database")
            return cls._get_client_mapping_from_db(mt5_login, customer_id)
            
        from shared_models.ib_commission.models import ClientIBMapping
        
        cache_key = cls.CLIENT_MAPPING_CACHE_KEY.format(
            mt5_login=mt5_login or "none",
            customer_id=customer_id
        )
        
        logger.info(f"Looking for cache key: {cache_key}")
        
        # Try to get from cache first
        mapping = cache.get(cache_key)
        if mapping:
            logger.info(f"Cache hit for {cache_key}")
            return mapping
        
        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, get from database
        mapping = cls._get_client_mapping_from_db(mt5_login, customer_id)
        
        if mapping:
            # Store in cache for future use
            logger.info(f"Storing in cache: {cache_key}")
            cache.set(cache_key, mapping, cls.CLIENT_MAPPING_CACHE_EXPIRY)
        
        return mapping
    
    @classmethod
    def _get_client_mapping_from_db(cls, mt5_login, customer_id):
        """Get client mapping directly from database"""
        from shared_models.ib_commission.models import ClientIBMapping
        
        logger.info(f"Fetching client mapping from DB for mt5_login={mt5_login}, customer_id={customer_id}")
        
        mapping = None
        if mt5_login:
            mapping = ClientIBMapping.objects.filter(
                mt5_login=mt5_login,
                customer_id=customer_id
            ).first()
        
        if not mapping and customer_id:
            # Try to find by customer only
            mapping = ClientIBMapping.objects.filter(
                customer_id=customer_id
            ).first()
        
        logger.info(f"Found client mapping in database: {mapping is not None}")
        return mapping
    
    @classmethod
    def invalidate_rule_cache(cls, agreement_id=None):
        """
        Invalidate rule cache for an agreement
        
        Args:
            agreement_id: The agreement ID (if None, invalidate all rule caches)
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping invalidation")
            return
            
        # Since we can't easily list keys in Django's cache framework,
        # we'll need to be more specific about which keys to invalidate
        if agreement_id:
            # Invalidate all commission types and symbols for this agreement
            for commission_type in ['COMMISSION', 'REBATE']:
                # Invalidate common symbols
                for symbol in ['*', None, 'EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']:
                    cache_key = cls.RULE_CACHE_KEY.format(
                        agreement_id=agreement_id,
                        symbol=symbol if symbol is not None else "none",
                        commission_type=commission_type
                    )
                    logger.info(f"Invalidating cache key: {cache_key}")
                    cache.delete(cache_key)
        else:
            # This is a more aggressive approach - clear the entire cache
            # Only use this if absolutely necessary
            logger.warning("Clearing entire cache")
            cache.clear()
    
    @classmethod
    def invalidate_agreement_cache(cls, customer_id):
        """
        Invalidate agreement cache for a customer
        
        Args:
            customer_id: The customer ID
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping invalidation")
            return
            
        cache_key = cls.AGREEMENT_CACHE_KEY.format(customer_id=customer_id)
        logger.info(f"Invalidating cache key: {cache_key}")
        cache.delete(cache_key)
    
    @classmethod
    def invalidate_hierarchy_cache(cls, customer_id):
        """
        Invalidate hierarchy cache for a customer
        
        Args:
            customer_id: The customer ID
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping invalidation")
            return
            
        cache_key = cls.HIERARCHY_CACHE_KEY.format(customer_id=customer_id)
        logger.info(f"Invalidating cache key: {cache_key}")
        cache.delete(cache_key)
    
    @classmethod
    def invalidate_client_mapping_cache(cls, mt5_login=None, customer_id=None):
        """
        Invalidate client mapping cache
        
        Args:
            mt5_login: The MT5 login
            customer_id: The customer ID
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping invalidation")
            return
            
        if mt5_login and customer_id:
            cache_key = cls.CLIENT_MAPPING_CACHE_KEY.format(
                mt5_login=mt5_login,
                customer_id=customer_id
            )
            logger.info(f"Invalidating cache key: {cache_key}")
            cache.delete(cache_key)
        elif customer_id:
            # If we only have customer_id, we'd need to invalidate all mt5_login mappings
            # This is a limitation of Django's cache framework - we can't easily list keys
            # A workaround would be to maintain a separate set of all mt5_logins for a customer
            # For now, we'll use a more aggressive approach
            logger.warning(f"Clearing entire cache due to customer_id-only invalidation request")
            cache.clear()
    
    @classmethod
    def list_all_cache_keys(cls):
        """
        List all cache keys (if possible)
        
        Returns:
            List of cache keys or None if not supported
        """
        try:
            # This only works with some cache backends like Redis
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'keys'):
                try:
                    all_keys = cache._cache.keys('*')
                    logger.info(f"Found {len(all_keys)} keys in cache")
                    return all_keys
                except:
                    logger.warning("Could not retrieve keys from cache")
                    return None
            else:
                logger.warning("Cache backend does not support listing keys")
                return None
        except Exception as e:
            logger.exception(f"Error listing cache keys: {e}")
            return None 