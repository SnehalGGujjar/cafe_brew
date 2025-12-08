from django.db import models
from django.utils import timezone
from django.urls import reverse
import uuid as _uuid

class Payment(models.Model):
    STATUS = [('pending','Pending'),('confirmed','Confirmed'),('failed','Failed')]
    uuid = models.UUIDField(default=_uuid.uuid4, editable=False, unique=True)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"Payment {self.uuid} ({self.status})"
    def payment_url(self, request=None):
        url = reverse('payments:pay', args=[self.uuid])
        return request.build_absolute_uri(url) if request else url
