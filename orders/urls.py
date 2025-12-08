from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name="orders"
urlpatterns=[ 
    path("start/", views.start_order, name="start"), path("add/<int:item_id>/", views.add_to_cart, name="add_to_cart"), 
    path("checkout/", views.checkout, name="checkout"), 
    path("thanks/<int:order_id>/", views.thanks, name="thanks"), 
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)