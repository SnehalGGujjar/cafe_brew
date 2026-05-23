from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path('', views.forecast_dashboard, name='forecast'),
    path('api/trigger-agent/', views.trigger_inventory_agent, name='trigger_agent'),
]
