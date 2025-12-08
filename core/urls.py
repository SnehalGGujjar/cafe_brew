from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "core"

urlpatterns = [
    path('', views.base, name='base'),
    path('about/', views.about, name='about'),
    path('team/', views.team, name='team'),
    
    path('scan/<slug:code>/', views.scan_redirect, name='scan'),
    path("locations.json", views.locations_json, name="locations_json"),
    path("set-location/", views.set_location, name="set_location"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)