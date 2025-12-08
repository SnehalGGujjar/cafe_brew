from django.contrib import admin, messages
from django import forms
from .models import *

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "lat", "lon", "is_active")
    list_filter = ("region", "is_active")
    search_fields = ("name", "region")
    list_editable = ("is_active",)
    ordering = ("region", "name")
    fieldsets = (
        ("Basic Info", {"fields": ("name", "region", "is_active")}),
        ("Coordinates", {"fields": ("lat", "lon")}),
    )
    actions = ["export_selected", "set_as_default_sitesetting"]

    def export_selected(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="locations.csv"'
        writer = csv.writer(response)
        writer.writerow(["Name", "Region", "Latitude", "Longitude", "Active"])
        for loc in queryset:
            writer.writerow([loc.name, loc.region, loc.lat, loc.lon, loc.is_active])
        return response
    export_selected.short_description = "Export selected locations as CSV"

    def set_as_default_sitesetting(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one location.", level=messages.ERROR)
            return
        loc = queryset.first()
        ss = SiteSetting.objects.first() or SiteSetting.objects.create()
        ss.default_lat, ss.default_lon = loc.lat, loc.lon
        ss.save()
        self.message_user(request, f"Default site location set to '{loc.name}'.", level=messages.SUCCESS)
    set_as_default_sitesetting.short_description = "Set as default SiteSetting location"


class SiteSettingForm(forms.ModelForm):
    default_from_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True).order_by("region", "name"),
        required=False,
        label="Set defaults from location",
        help_text="Choose a location to copy its latitude/longitude below.",
    )

    class Meta:
        model = SiteSetting
        fields = ("default_from_location", "default_lat", "default_lon")

    def save(self, commit=True):
        inst = super().save(commit=False)
        loc = self.cleaned_data.get("default_from_location")
        if loc:
            inst.default_lat = loc.lat
            inst.default_lon = loc.lon
        if commit:
            inst.save()
        return inst


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    form = SiteSettingForm
    list_display = ("id", "default_lat", "default_lon", "get_location_match")
    fieldsets = (
        (None, {
            "fields": ("default_from_location", "default_lat", "default_lon"),
            "description": "Pick a location to auto-fill, or set custom coordinates."
        }),
    )

    def get_location_match(self, obj):
        match = Location.objects.filter(lat=obj.default_lat, lon=obj.default_lon).first()
        return match.name if match else "—"
    get_location_match.short_description = "Matching Location"

from django.utils.html import format_html

@admin.register(SitePayment)
class SitePaymentAdmin(admin.ModelAdmin):
    list_display = ("qr_preview", "payment_link", "updated_at")
    readonly_fields = ("updated_at",)

    def qr_preview(self, obj):
        if obj.qr_image:
            return format_html('<img src="{}" style="height:80px;border-radius:6px"/>', obj.qr_image.url)
        return "—"
    qr_preview.short_description = "QR"
