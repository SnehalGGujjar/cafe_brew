from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError

from core.models import SiteSetting, Location
from .models import Item, MenuRule
from .utils import get_weather


def today_menu(request):
    """Show today's menu filtered using DB default location."""
    try:
        site = SiteSetting.get_solo()
        lat, lon = site.default_lat, site.default_lon

        # Try matching the nearest Location by coordinates
        loc = (
            Location.objects.filter(lat=lat, lon=lon, is_active=True).first()
            or Location.objects.filter(is_active=True).first()
        )
        location_name = loc.name if loc else "Default Location"
        label = f"{location_name} ({lat:.4f}, {lon:.4f})"
    except (OperationalError, ProgrammingError):
        lat = getattr(settings, "WEATHER_DEFAULT_LAT", 12.9716)
        lon = getattr(settings, "WEATHER_DEFAULT_LON", 77.5946)
        location_name = "System Default"
        label = f"{location_name} ({lat:.4f}, {lon:.4f})"

    # Override with session-based location if set by GPS
    session_lat = request.session.get("geo_lat")
    session_lon = request.session.get("geo_lon")
    session_label = request.session.get("geo_label")
    if session_lat is not None and session_lon is not None:
        lat, lon = float(session_lat), float(session_lon)
        location_name = session_label or "Your Location"
        label = session_label or f"GPS ({lat:.4f}, {lon:.4f})"

    condition, weather = get_weather(lat, lon)

    # Filter menu items by condition
    items_qs = Item.objects.filter(is_active=True)
    if condition == "any":
        filtered = list(items_qs)
    else:
        allowed_ids = set(MenuRule.objects.filter(condition__in=[condition, "any"])
                          .values_list("item_id", flat=True))
        filtered = [i for i in items_qs if (not i.rules.exists()) or (i.id in allowed_ids)]

    return render(request, "menu/today.html", {
        "items": filtered,
        "condition": condition,
        "weather": weather,
        "lat": lat,
        "lon": lon,
        "location_label": label,
        "location_name": location_name,
    })

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def ai_concierge_api(request):
    """Simulated Agentic AI Concierge endpoint."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').lower()
            
            # Simulated NLP keyword extraction and reasoning
            # Instead of strict Q objects, we will score items based on keywords.
            items = list(Item.objects.filter(is_active=True))
            
            # Keywords
            is_vegan = 'vegan' in message or 'veg' in message
            is_cold = 'cold' in message or 'ice' in message or 'refreshing' in message or 'chill' in message
            is_hot = 'hot' in message or 'warm' in message or 'heat' in message
            is_food = 'food' in message or 'eat' in message or 'hungry' in message
            is_drink = 'drink' in message or 'beverage' in message or 'thirsty' in message
            is_sweet = 'sweet' in message or 'dessert' in message
            is_coffee = 'coffee' in message or 'caffeine' in message or 'espresso' in message
            is_spicy = 'spicy' in message or 'hot' in message
            
            best_item = None
            best_score = -1
            
            for item in items:
                score = 0
                name_desc = (item.name + " " + item.description).lower()
                
                # Positive scoring
                if is_vegan and ('vegan' in name_desc or 'salad' in name_desc or 'veg' in name_desc): score += 5
                if is_cold and ('ice' in name_desc or 'cold' in name_desc or 'slush' in name_desc): score += 5
                if is_hot and ('hot' in name_desc or 'warm' in name_desc or 'soup' in name_desc): score += 5
                if is_food and item.category == 'food': score += 3
                if is_drink and item.category == 'drink': score += 3
                if is_sweet and (item.category == 'dessert' or 'sweet' in name_desc): score += 4
                if is_coffee and ('coffee' in name_desc or 'espresso' in name_desc or 'latte' in name_desc): score += 5
                if is_spicy and 'spic' in name_desc: score += 4
                
                # Negative scoring (penalties)
                if is_cold and ('hot' in name_desc or 'warm' in name_desc or 'soup' in name_desc): score -= 10
                if is_hot and ('ice' in name_desc or 'cold' in name_desc or 'chill' in name_desc): score -= 10
                if is_vegan and ('chicken' in name_desc or 'cheese' in name_desc or 'paneer' in name_desc or 'egg' in name_desc or 'milk' in name_desc): score -= 10
                if is_food and item.category != 'food': score -= 5
                if is_drink and item.category != 'drink': score -= 5
                
                # If there are no specific keywords, pick a random popular item (score will be 0)
                if score > best_score:
                    best_score = score
                    best_item = item

            # If user typed keywords but no item scored > 0, it means we have no match.
            has_keywords = any([is_vegan, is_cold, is_hot, is_food, is_drink, is_sweet, is_coffee, is_spicy])
            
            if best_item and (not has_keywords or best_score > 0):
                response_text = f"I think you'll love our **{best_item.name}**! Shall I add it to your cart?"
                return JsonResponse({
                    'ok': True,
                    'text': response_text,
                    'item_id': best_item.id,
                    'item_name': best_item.name,
                    'item_price': str(best_item.price)
                })
            else:
                return JsonResponse({
                    'ok': True,
                    'text': "I don't think we have exactly that right now. How about checking our main menu?",
                    'item_id': None
                })
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'ok': False, 'error': str(e)})
            
    return JsonResponse({'ok': False, 'error': 'Invalid request'})
