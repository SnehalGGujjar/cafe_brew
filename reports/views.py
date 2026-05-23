import json
from django.shortcuts import render
from django.db.models import Sum, F, Count
from django.db.models.functions import ExtractHour
from orders.models import Order, OrderItem
from core.models import AIConfiguration

def dashboard(request):
    ai_config = AIConfiguration.get_solo()
    # Base Querysets
    orders = Order.objects.exclude(status='cart')
    paid_orders = orders.filter(status__in=['paid', 'completed'])
    
    total_orders = orders.count()
    revenue = paid_orders.aggregate(s=Sum('total'))['s'] or 0

    # 1. Top Items
    top = (
        OrderItem.objects
        .values(name=F('item__name'))
        .annotate(qty=Sum('qty'))
        .order_by('-qty')[:5]
    )
    top_labels = [t['name'] for t in top]
    top_values = [t['qty'] for t in top]
    top_pairs  = list(zip(top_labels, top_values))

    # 2. Revenue by Weather
    weather_stats = (
        paid_orders
        .exclude(weather_condition__isnull=True)
        .values('weather_condition')
        .annotate(total_revenue=Sum('total'))
        .order_by('-total_revenue')
    )
    weather_labels = [w['weather_condition'] for w in weather_stats]
    weather_values = [float(w['total_revenue']) for w in weather_stats]

    # 3. Busiest Hours (Time-of-day analytics)
    hourly_stats = (
        paid_orders
        .annotate(hour=ExtractHour('created_at'))
        .values('hour')
        .annotate(order_count=Count('id'))
        .order_by('hour')
    )
    
    # Fill in a 24-hour array
    hours = [f"{h}:00" for h in range(7, 22)] # Cafe hours: 7 AM to 9 PM
    hour_counts = [0] * len(hours)
    
    busiest_hour = None
    max_orders = -1
    
    for stat in hourly_stats:
        hr = stat['hour']
        if 7 <= hr <= 21:
            idx = hr - 7
            hour_counts[idx] = stat['order_count']
            if stat['order_count'] > max_orders:
                max_orders = stat['order_count']
                busiest_hour = f"{hr}:00 - {hr+1}:00"

    # 4. Generate "AI" Insights based on data
    insights = []
    
    if weather_stats:
        top_weather = weather_stats[0]
        bottom_weather = weather_stats[-1] if len(weather_stats) > 1 else None
        
        insights.append(
            f"Most of your revenue (${float(top_weather['total_revenue']):.2f}) comes on {top_weather['weather_condition']} days. "
            f"Make sure to fully staff the cafe when the forecast calls for {top_weather['weather_condition']} weather."
        )
        if bottom_weather and top_weather['weather_condition'] != bottom_weather['weather_condition']:
            insights.append(
                f"Revenue drops significantly on {bottom_weather['weather_condition']} days. "
                f"Recommendation: Automatically trigger a 'Comfort Food Discount' push notification when it is {bottom_weather['weather_condition']} to boost sales."
            )
            
    if busiest_hour:
        insights.append(
            f"Your peak rush hour is exactly between {busiest_hour}. Ensure your Kitchen Display System is actively monitored and prep stations are fully stocked right before this window."
        )

    return render(request, 'reports/dashboard.html', {
        'total_orders': total_orders,
        'revenue': revenue,
        'top_labels': json.dumps(top_labels),
        'top_values': json.dumps(top_values),
        'top_pairs':  top_pairs,
        
        # New Predictive Data
        'weather_labels': json.dumps(weather_labels),
        'weather_values': json.dumps(weather_values),
        'hours': json.dumps(hours),
        'hour_counts': json.dumps(hour_counts),
        'insights': insights,
        'ai_config': ai_config
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def toggle_pricing_ai(request):
    """API to toggle Dynamic AI Pricing on or off."""
    if request.method == 'POST':
        from core.models import AIConfiguration
        ai_config = AIConfiguration.get_solo()
        ai_config.dynamic_pricing_enabled = not ai_config.dynamic_pricing_enabled
        
        # If enabling, simulate a 15% surge
        if ai_config.dynamic_pricing_enabled:
            ai_config.surge_multiplier = 1.15
        else:
            ai_config.surge_multiplier = 1.00
            
        ai_config.save()
        return JsonResponse({
            'ok': True, 
            'enabled': ai_config.dynamic_pricing_enabled,
            'multiplier': float(ai_config.surge_multiplier)
        })
    return JsonResponse({'ok': False})
