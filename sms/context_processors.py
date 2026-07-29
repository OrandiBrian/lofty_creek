from .services import get_sms_balance
from django.core.cache import cache

def balance_processor(request):
    """
    Context processor to fetch and include SMS balance for staff users inside SMS portal path.
    """
    if request.user.is_authenticated and request.user.is_staff and request.path.startswith('/sms/'):
        balance = cache.get('sms-account-balance')
        if balance is None:
            balance = get_sms_balance()
            cache.set('sms-account-balance', balance, 300)
        return {'navbar_balance': balance}
    return {}
