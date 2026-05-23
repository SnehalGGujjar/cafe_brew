from django.db import models

class Item(models.Model):
    CATEGORY_CHOICES = [('food','Food'),('drink','Drink'),('dessert','Dessert')]
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct URL to a real food image (e.g., from Unsplash)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='food')
    is_active = models.BooleanField(default=True)
    
    @property
    def display_price(self):
        """Returns the dynamically adjusted price if AI Surge Pricing is enabled."""
        from core.models import AIConfiguration
        ai_config = AIConfiguration.get_solo()
        if ai_config.dynamic_pricing_enabled and ai_config.surge_multiplier > 1.0:
            return round(self.price * ai_config.surge_multiplier, 2)
        return self.price
        
    def __str__(self): return self.name

class MenuRule(models.Model):
    CONDITION_CHOICES = [('any','Any'),('hot','Hot day'),('cold','Cold day'),('rain','Rainy'),('clear','Clear/Normal')]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='rules')
    condition = models.CharField(max_length=16, choices=CONDITION_CHOICES, default='any')
    def __str__(self): return f"{self.item.name} -> {self.condition}"
