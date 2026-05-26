from .services import get_sms_balance

def balance_processor(request):
    """
    Context processor to fetch and include SMS balance for staff users inside SMS portal path.
    """
    if request.user.is_authenticated and request.user.is_staff and request.path.startswith('/sms/'):
        return {
            'navbar_balance': get_sms_balance()
        }
    return {}
