from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from .models import Location

# Simple base view (optional)
def base(request):
    return render(request, 'base.html')

def about(request):
    return render(request, 'about/about.html')

def team(request):
    return render(request, 'about/team.html')


def locations_json(request):
    """
    Returns grouped active locations:
    { ok: true, groups: [{region, region_label, items:[{id,name,lat,lon}]}] }
    """
    groups = []
    order = ["Cold", "HotDry", "Coastal", "Central", "EastNE", "South", "UT", "Other"]
    labels = dict(Location.REGION_CHOICES)

    for key in order:
        qs = Location.objects.filter(is_active=True, region=key).order_by("name")
        if not qs.exists():
            continue
        items = [{"id": x.id, "name": x.name, "lat": x.lat, "lon": x.lon} for x in qs]
        groups.append({"region": key, "region_label": labels.get(key, key), "items": items})

    return JsonResponse({"ok": True, "groups": groups})

@require_POST
@csrf_protect
def set_location(request):
    """
    Accepts:
    - location_id (preferred) -> sets session to that location
    - or lat, lon (custom) and optional label
    """
    location_id = request.POST.get("location_id")
    if location_id:
        try:
            loc = Location.objects.get(pk=location_id, is_active=True)
            request.session["geo_location_id"] = loc.id
            request.session["geo_lat"] = loc.lat
            request.session["geo_lon"] = loc.lon
            request.session["geo_label"] = loc.name
            return JsonResponse({"ok": True, "label": loc.name, "lat": loc.lat, "lon": loc.lon})
        except Location.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Invalid location."}, status=400)

    # fallback: custom coordinates
    try:
        lat = float(request.POST.get("lat"))
        lon = float(request.POST.get("lon"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid coordinates."}, status=400)

    label = request.POST.get("label") or "Custom location"
    request.session["geo_location_id"] = None
    request.session["geo_lat"] = lat
    request.session["geo_lon"] = lon
    request.session["geo_label"] = label
    return JsonResponse({"ok": True, "label": label, "lat": lat, "lon": lon})

def scan_redirect(request, code):
    request.session['table_code'] = code
    return redirect('menu:today')
