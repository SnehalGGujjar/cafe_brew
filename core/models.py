from django.db import models

class Location(models.Model):
    REGION_CHOICES = [
        ("Cold", "Cold Regions / Hill Stations"),
        ("HotDry", "Hot & Dry Regions"),
        ("Coastal", "Moderate / Coastal Regions"),
        ("Central", "Central / Plateau Regions"),
        ("EastNE", "Eastern & North-Eastern Regions"),
        ("South", "Southern Tropical Regions"),
        ("UT", "Union Territories"),
        ("Other", "Other"),
    ]
    name = models.CharField(max_length=120, unique=True)
    region = models.CharField(max_length=16, choices=REGION_CHOICES, default="Other")
    lat = models.FloatField()
    lon = models.FloatField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["region", "name"]

    def __str__(self):
        return f"{self.name} ({self.lat:.4f}, {self.lon:.4f})"


class SiteSetting(models.Model):
    default_lat = models.FloatField(default=12.9716)
    default_lon = models.FloatField(default=77.5946)

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1, defaults={"default_lat": 12.9716, "default_lon": 77.5946}
        )
        return obj

class SitePayment(models.Model):
    """
    Single, admin-managed QR image (and optional link) used for ALL orders.
    Admin can change this anytime.
    """
    qr_image = models.ImageField(upload_to="payment_qr/", blank=True, null=True)
    payment_link = models.URLField(blank=True, null=True, help_text="Optional: where 'Open Payment URL' should go")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Global Payment QR"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj