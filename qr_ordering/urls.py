from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from analytics.admin_views import admin_analytics

urlpatterns = [
    path('accounts/', include('accounts.urls')),

    # path('admin/', admin.site.urls),
    path("admin/analytics/", admin_analytics, name="admin_analytics"),
    path("admin/", admin.site.urls),
    
    path('', RedirectView.as_view(pattern_name='core:base', permanent=False)),
    path('core/', include('core.urls')),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
    path('feedback/', include('feedback.urls')),
    path('inventory/', include('inventory.urls')),
]
