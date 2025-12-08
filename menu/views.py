from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError

from core.models import SiteSetting, Location
from .models import Item

import requests

def get_weather(lat, lon):
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,weather_code"
        )
        r = requests.get(url, timeout=6)
        data = r.json()
        if isinstance(data, dict) and data.get("error"):
            return "any", {"temperature": None, "precipitation": None, "weather_code": None}

        cur = data.get("current", {}) or {}
        t = cur.get("temperature_2m")
        p = cur.get("precipitation")
        t = float(t) if t is not None else None
        p = float(p) if p is not None else None

        if p is not None and p >= 0.5: cond = "rain"
        elif t is not None and t >= 32: cond = "hot"
        elif t is not None and t <= 18: cond = "cold"
        elif t is None and p is None:  cond = "any"
        else:                           cond = "clear"

        return cond, {"temperature": t, "precipitation": p, "weather_code": cur.get("weather_code")}
    except Exception:
        return "any", {"temperature": None, "precipitation": None, "weather_code": None}

# menu/views.py
from django.shortcuts import render
from core.models import SiteSetting, Location
from .models import Item, MenuRule
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError
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
