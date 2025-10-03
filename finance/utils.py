# finance/utils.py
from django.db.models import Sum
from .models import Transaction

def aggregate_by_period(start=None, end=None, branch=None):
    """
    Returns a dict with totals for revenue, expense, and net between start and end datetimes.
    If start/end are None, use all available.
    """
    qs = Transaction.objects.all()
    if start:
        qs = qs.filter(created_at__gte=start)
    if end:
        qs = qs.filter(created_at__lte=end)
    if branch:
        qs = qs.filter(branch=branch)

    revenue = qs.filter(transaction_type='revenue').aggregate(total=Sum('total_amount'))['total'] or 0
    expense = qs.filter(transaction_type='expense').aggregate(total=Sum('total_amount'))['total'] or 0
    net = revenue - expense
    return {
        'revenue': revenue,
        'expense': expense,
        'net': net
    }