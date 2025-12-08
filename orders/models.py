from django.db import models
from django.utils import timezone
from menu.models import Item

class Order(models.Model):
    STATUS = [('cart','Cart'),('pending','Pending Payment'),('paid','Paid'),('completed','Completed'),('cancelled','Cancelled')]
    customer_email = models.EmailField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=16, choices=STATUS, default='cart')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def recalc_total(self):
        total = sum([oi.subtotal() for oi in self.items.all()])
        self.total = total; return total
    def __str__(self): return f"Order #{self.id} {self.customer_email} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    def subtotal(self): return self.qty * self.unit_price
    def __str__(self): return f"{self.item.name} x{self.qty}"
