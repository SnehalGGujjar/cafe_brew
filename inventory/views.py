import json
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from .models import InventoryItem
from menu.models import MenuRule
from core.models import AIConfiguration
import random

@staff_member_required
def forecast_dashboard(request):
    items = InventoryItem.objects.select_related('item').all().order_by('stock')
    
    # 1. Low stock items
    low_stock_items = [i for i in items if i.stock <= i.reorder_level]
    healthy_items = [i for i in items if i.stock > i.reorder_level]
    
    # Calculate capped percentages for the UI so we don't need complex logic in the template
    for i in low_stock_items:
        i.stock_percentage = min(100, int((i.stock / max(1, i.reorder_level + 20)) * 100))
    for i in healthy_items:
        i.stock_percentage = min(100, i.stock)
    
    # 2. AI Forecasting Simulation
    # For a real app, this would use a weather API and historical sales data.
    # Here, we simulate it based on a "Predicted Weather" for tomorrow.
    weather_conditions = [
        ("Cold & Rainy", "cold", "Increase hot drinks, soups, and comfort food by 25%."),
        ("Hot & Sunny", "hot", "Increase cold beverages, ice creams, and salads by 30%."),
        ("Mild & Pleasant", "any", "Standard weekend rush expected. Maintain baseline stock.")
    ]
    
    tomorrow_weather, target_condition, advice = random.choice(weather_conditions)
    
    # Find items that match the target condition to recommend restocking
    recommended_restock = []
    if target_condition != "any":
        rules = MenuRule.objects.filter(condition=target_condition).select_related('item__inventory')
        recommended_restock = [rule.item.inventory for rule in rules if hasattr(rule.item, 'inventory')]
        # Sort by lowest stock first
        recommended_restock = sorted(recommended_restock, key=lambda x: x.stock)[:6] # Top 6 to restock
    
    return render(request, 'inventory/forecast.html', {
        'low_stock_items': low_stock_items,
        'healthy_items': healthy_items,
        'tomorrow_weather': tomorrow_weather,
        'advice': advice,
        'recommended_restock': recommended_restock,
        'total_items': len(items),
        'low_stock_count': len(low_stock_items)
    })

@csrf_exempt
def trigger_inventory_agent(request):
    """Triggers the autonomous agent management command from the UI."""
    if request.method == 'POST':
        try:
            call_command('run_inventory_agent')
            ai_config = AIConfiguration.get_solo()
            report = {}
            if ai_config.last_inventory_order:
                report = json.loads(ai_config.last_inventory_order)
                
            return JsonResponse({'ok': True, 'report': report})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})
    return JsonResponse({'ok': False})
