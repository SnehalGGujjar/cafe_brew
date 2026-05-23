from django.urls import path
from . import views
app_name="menu"
urlpatterns=[ 
    path("today/", views.today_menu, name="today"), 
    path("api/chat/", views.ai_concierge_api, name="ai_chat"),
]
