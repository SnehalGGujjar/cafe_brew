from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("created_at", "rating", "email", "order")
    list_filter = ("rating", "created_at")
    search_fields = ("email", "comment")
