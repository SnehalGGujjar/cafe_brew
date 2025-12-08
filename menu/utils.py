# menu/utils.py
import requests

def get_weather(lat, lon):
    """
    Calls Open-Meteo and maps current conditions to one of:
    'any', 'hot', 'cold', 'rain', 'clear'
    Returns: (condition, {"temperature": t or None, "precipitation": p or None, "weather_code": code or None})
    """
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,weather_code"
        )
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get("error"):
            return "any", {"temperature": None, "precipitation": None, "weather_code": None}

        cur = data.get("current", {}) or {}
        # sensible defaults if missing
        t = cur.get("temperature_2m")
        p = cur.get("precipitation")
        t = float(t) if t is not None else None
        p = float(p) if p is not None else None

        if p is not None and p >= 0.5:
            cond = "rain"
        elif t is not None and t >= 32:
            cond = "hot"
        elif t is not None and t <= 18:
            cond = "cold"
        elif t is None and p is None:
            cond = "any"   # API fallback → show all active items
        else:
            cond = "clear"

        return cond, {"temperature": t, "precipitation": p, "weather_code": cur.get("weather_code")}
    except Exception:
        return "any", {"temperature": None, "precipitation": None, "weather_code": None}
