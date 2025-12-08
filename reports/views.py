from django.shortcuts import render
from django.db.models import Sum, F
from orders.models import Order, OrderItem

def dashboard(request):
    total_orders = Order.objects.exclude(status='cart').count()
    revenue = Order.objects.filter(status__in=['paid','completed']).aggregate(s=Sum('total'))['s'] or 0
    top = (OrderItem.objects.values(name=F('item__name')).annotate(qty=Sum('qty')).order_by('-qty')[:5])
    top_labels = [t['name'] for t in top]
    top_values = [t['qty'] for t in top]
    return render(request, 'reports/dashboard.html', {'total_orders': total_orders,'revenue': revenue,'top_labels': top_labels,'top_values': top_values})
