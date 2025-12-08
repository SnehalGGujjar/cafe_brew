# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from decimal import Decimal
from menu.models import Item, MenuRule

ITEMS = [
    # -------- any (always allowed) --------
    {"name":"Veg Burger","desc":"Crispy patty, fresh veggies","price":"120","cat":"food","conds":["any"]},
    {"name":"French Fries","desc":"Crispy golden fries","price":"75","cat":"food","conds":["any"]},
    {"name":"Gulab Jamun","desc":"Traditional Indian sweet","price":"80","cat":"dessert","conds":["any"]},
    {"name":"Masala Dosa","desc":"South Indian classic with potato filling","price":"100","cat":"food","conds":["any"]},

    # -------- clear / normal --------
    {"name":"Paneer Sandwich","desc":"Grilled sandwich with paneer filling","price":"110","cat":"food","conds":["clear","any"]},
    {"name":"Cold Coffee","desc":"Chilled, lightly sweetened","price":"90","cat":"drink","conds":["clear"]},
    {"name":"Margherita Pizza","desc":"Cheesy classic pizza with basil","price":"220","cat":"food","conds":["clear"]},

    # -------- hot --------
    {"name":"Watermelon Cooler","desc":"Fresh juice with mint","price":"70","cat":"drink","conds":["hot"]},
    {"name":"Buttermilk (Chaas)","desc":"Spiced & refreshing","price":"40","cat":"drink","conds":["hot"]},
    {"name":"Cucumber Salad","desc":"Lemon, pepper, herbs","price":"95","cat":"food","conds":["hot"]},
    {"name":"Kulfi","desc":"Malai kulfi stick","price":"60","cat":"dessert","conds":["hot"]},

    # -------- cold --------
    {"name":"Tomato Soup","desc":"Creamy & warm","price":"90","cat":"food","conds":["cold"]},
    {"name":"Masala Tea","desc":"Hot, spiced chai","price":"25","cat":"drink","conds":["cold"]},
    {"name":"Veg Pulao","desc":"Steaming rice, mild spices","price":"130","cat":"food","conds":["cold"]},
    {"name":"Brownie with Hot Chocolate","desc":"Warm, gooey dessert","price":"140","cat":"dessert","conds":["cold"]},

    # -------- rain --------
    {"name":"Onion Pakora","desc":"Crispy fritters","price":"85","cat":"food","conds":["rain"]},
    {"name":"Samosa (2 pcs)","desc":"Potato & peas","price":"60","cat":"food","conds":["rain"]},
    {"name":"Cutting Chai","desc":"Garam chai in a glass","price":"15","cat":"drink","conds":["rain"]},
    {"name":"Paneer Bhurji Pav","desc":"Hot, buttery pav","price":"95","cat":"food","conds":["rain"]},
]

class Command(BaseCommand):
    help = "Seed demo menu items & weather rules"

    def handle(self, *args, **opts):
        created = 0
        for row in ITEMS:
            item, _new = Item.objects.get_or_create(
                name=row["name"],
                defaults={
                    "description": row["desc"],
                    "price": Decimal(row["price"]),
                    "category": row["cat"],
                    "is_active": True,
                },
            )
            # ensure description/price kept in sync if re-running
            item.description = row["desc"]
            item.price = Decimal(row["price"])
            item.category = row["cat"]
            item.is_active = True
            item.save()

            # attach rules
            MenuRule.objects.filter(item=item).exclude(condition="any").delete()
            for cond in row["conds"]:
                MenuRule.objects.get_or_create(item=item, condition=cond)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded/updated {created} items with rules."))
