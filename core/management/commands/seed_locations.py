# core/management/commands/seed_locations.py
from django.core.management.base import BaseCommand
from core.models import Location

DATA = [
    # region, name, lat, lon
    ("Cold", "Jammu", 32.7266, 74.8570),
    ("Cold", "Srinagar", 34.0837, 74.7973),
    ("Cold", "Manali", 32.2432, 77.1892),
    ("Cold", "Nainital", 30.0668, 79.0193),
    ("Cold", "Shimla", 31.1048, 77.1734),
    ("Cold", "Gangtok", 27.3389, 88.6065),
    ("Cold", "Shillong", 25.5788, 91.8933),
    ("Cold", "Delhi (Winter Cold)", 28.6139, 77.2090),

    ("HotDry", "Jaipur", 26.9124, 75.7873),
    ("HotDry", "Kota", 25.2138, 75.8648),
    ("HotDry", "Ajmer", 26.4499, 74.6399),
    ("HotDry", "Udaipur", 24.5854, 73.7125),
    ("HotDry", "Surat", 21.1702, 72.8311),
    ("HotDry", "Vadodara", 22.3072, 73.1812),
    ("HotDry", "Ahmedabad", 23.0225, 72.5714),
    ("HotDry", "Gurugram", 28.4089, 77.3178),
    ("HotDry", "Lucknow (Hot Summer)", 26.8467, 80.9462),

    ("Coastal", "Bengaluru", 12.9716, 77.5946),
    ("Coastal", "Chennai", 13.0827, 80.2707),
    ("Coastal", "Mumbai", 19.0760, 72.8777),
    ("Coastal", "Goa", 15.2993, 74.1240),
    ("Coastal", "Hyderabad", 17.3850, 78.4867),
    ("Coastal", "Coimbatore", 11.0168, 76.9558),
    ("Coastal", "Kochi", 9.9312, 76.2673),
    ("Coastal", "Thiruvananthapuram", 8.5241, 76.9366),
    ("Coastal", "Vijayawada", 16.5062, 80.6480),
    ("Coastal", "Visakhapatnam", 17.6868, 83.2185),

    ("Central", "Pune", 18.5204, 73.8567),
    ("Central", "Nashik", 19.9975, 73.7898),
    ("Central", "Nagpur", 21.1458, 79.0882),
    ("Central", "Bhopal", 23.2599, 77.4126),
    ("Central", "Indore", 22.7196, 75.8577),
    ("Central", "Raipur", 21.2514, 81.6296),
    ("Central", "Aurangabad", 19.8762, 75.3433),

    ("EastNE", "Kolkata", 22.5726, 88.3639),
    ("EastNE", "Guwahati", 26.1445, 91.7362),
    ("EastNE", "Patna", 25.4670, 85.9782),
    ("EastNE", "Imphal", 24.8170, 93.9368),
    ("EastNE", "Aizawl", 23.1645, 92.9376),
    ("EastNE", "Itanagar", 27.4712, 94.9111),
    ("EastNE", "Agartala", 23.8315, 91.2868),
    ("EastNE", "Dhanbad", 23.7957, 86.4304),
    ("EastNE", "Jamshedpur", 22.8046, 86.2029),

    ("South", "Tiruchirappalli", 10.7905, 78.7047),
    ("South", "Mysuru", 12.2958, 76.6394),
    ("South", "Kozhikode", 11.2588, 75.7804),
    ("South", "Ballari", 15.1394, 76.9214),
    ("South", "Belagavi (Belgaum)", 15.8497, 74.4977),
    ("South", "Alappuzha", 9.4981, 76.3388),
    ("South", "Guntur", 16.3067, 80.4365),

    ("UT", "Puducherry", 11.9416, 79.8083),
    ("UT", "Daman", 20.4283, 72.8397),
    ("UT", "Karaikal", 9.9252, 78.1198),
    ("UT", "Chandigarh", 30.7333, 76.7794),
    ("UT", "Diu", 20.7140, 70.9870),   # adjusted to Diu’s typical coords
    ("UT", "New Delhi (NCT)", 28.6139, 77.2090),
    ("UT", "Port Blair (Andaman & Nicobar)", 11.6234, 92.7265),
    ("UT", "Yanam", 16.7331, 82.2135),
]

class Command(BaseCommand):
    help = "Seed preset Indian locations into core_location"

    def handle(self, *args, **kwargs):
        created = 0
        for region, name, lat, lon in DATA:
            obj, was_created = Location.objects.update_or_create(
                name=name,
                defaults={"region": region, "lat": lat, "lon": lon, "is_active": True},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} locations."))
