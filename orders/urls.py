from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name="orders"
urlpatterns=[ 
    path("start/", views.start_order, name="start"), path("add/<int:item_id>/", views.add_to_cart, name="add_to_cart"), 
    path("checkout/", views.checkout, name="checkout"), 
    path("thanks/<int:order_id>/", views.thanks, name="thanks"), 
    
    # Kitchen Display System
    path("kitchen/", views.kds_dashboard, name="kds_dashboard"),
    path("kitchen/api/orders/", views.kds_api_orders, name="kds_api_orders"),
    path("kitchen/api/update/", views.kds_update_item, name="kds_update_item"),
    
    # Customer Realtime Status
    path("api/status/<int:order_id>/", views.order_status_api, name="order_status_api"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)