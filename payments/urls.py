from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("pay/<uuid:uuid>/", views.pay, name="pay"),
    path("confirm/<uuid:uuid>/", views.confirm, name="confirm"),
    path("status/<uuid:uuid>/", views.payment_status, name="status"),
    # payments/urls.py
    path("mark-failed/<uuid:uuid>/", views.mark_failed, name="mark_failed"),

]
