from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.models import Group

# ✅ Remove "Groups" from admin
admin.site.unregister(Group)

# Register your models here.
admin.site.site_header  = "QR Café Admin"
admin.site.site_title   = "QR Café Admin"
admin.site.index_title  = "Welcome to Admin"