from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from inventory.models import InventoryItem
from core.models import AIConfiguration
import json

class Command(BaseCommand):
    help = 'Runs the Autonomous AI Inventory Agent'

    def handle(self, *args, **kwargs):
        self.stdout.write("Waking up AI Inventory Agent...")
        
        # 1. Check Low Stock Items
        low_items = InventoryItem.objects.filter(stock__lte=models.F('reorder_level'))
        if not low_items.exists():
            self.stdout.write("No low stock detected. Agent going back to sleep.")
            return

        # 2. Simulate AI Reasoning
        purchase_orders = []
        for inv in low_items:
            po = {
                'item': inv.item.name,
                'current_stock': inv.stock,
                'reorder_level': inv.reorder_level,
                'order_qty': max(50, inv.reorder_level * 2),
                'reason': f"Stock is critically low ({inv.stock}). Simulated weather forecast shows high demand for {inv.item.get_category_display()}s tomorrow."
            }
            purchase_orders.append(po)
            
            # Auto-replenish stock to simulate the supplier fulfilling the order
            inv.stock += po['order_qty']
            inv.save()
            
        # 3. Generate Report
        report = {
            'timestamp': timezone.now().isoformat(),
            'orders': purchase_orders,
            'summary': f"Autonomously generated Purchase Orders for {len(purchase_orders)} items. Stock has been auto-replenished."
        }
        
        # 4. Save to AI Configuration
        ai_config = AIConfiguration.get_solo()
        ai_config.last_inventory_order = json.dumps(report)
        ai_config.save()
        
        self.stdout.write(self.style.SUCCESS(f"Agent finished. Processed {len(purchase_orders)} items."))
