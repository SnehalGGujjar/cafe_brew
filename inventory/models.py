from django.db import models
from menu.models import Item
class InventoryItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='inventory')
    stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    def __str__(self): return f"{self.item.name} stock={self.stock}"
