# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name="myapp"

urlpatterns = [
    path('about/', about, name='about'),
    

    path('messages/', user_list_view, name='user_list'),
    path('messages/<int:user_id>/', chat_view_by_id, name='chat'),
    
    path('feedback/', feedback_view, name='feedback'),
    path('feedbacks/', view_feedbacks, name='view_feedbacks'),

    

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

