from django.urls import path
from . import views
app_name="reports"
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/toggle-pricing-ai/', views.toggle_pricing_ai, name='toggle_pricing_ai'),
]
