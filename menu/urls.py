from django.urls import path
from . import views
app_name="menu"
urlpatterns=[ path("today/", views.today_menu, name="today"), ]
