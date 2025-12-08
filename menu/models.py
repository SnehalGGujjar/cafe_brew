from django.db import models

class Item(models.Model):
    CATEGORY_CHOICES = [('food','Food'),('drink','Drink'),('dessert','Dessert')]
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='food')
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class MenuRule(models.Model):
    CONDITION_CHOICES = [('any','Any'),('hot','Hot day'),('cold','Cold day'),('rain','Rainy'),('clear','Clear/Normal')]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='rules')
    condition = models.CharField(max_length=16, choices=CONDITION_CHOICES, default='any')
    def __str__(self): return f"{self.item.name} -> {self.condition}"
