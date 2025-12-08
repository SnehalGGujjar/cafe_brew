from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone


@staff_member_required
def admin_analytics(request):
    # Lazy import to avoid issues during migrate
    try:
        from orders.models import Order, OrderItem
    except Exception:
        Order = OrderItem = None

    ctx = {"title": "Analytics (Last 30 days)"}

    if Order is not None:
        PAID_STATES = ("paid", "completed", "success", "fulfilled")

        today = timezone.now()
        start = today - timedelta(days=30)

        base = Order.objects.filter(created_at__gte=start, status__in=PAID_STATES)

        # KPIs
        kpis = base.aggregate(
            revenue=Sum("total"),
            orders=Count("id"),
            users=Count("customer_email", distinct=True),
        )
        revenue = kpis.get("revenue") or 0
        orders = kpis.get("orders") or 0
        users = kpis.get("users") or 0
        aov = (revenue / orders) if orders else 0

        # By day
        by_day = (
            base.annotate(day=TruncDate("created_at"))
                .values("day")
                .annotate(day_revenue=Sum("total"), day_orders=Count("id"))
                .order_by("day")
        )

        # ---- SAFE pattern for sales aggregation ----
        # 1) annotate each OrderItem with a non-aggregate row-level expression
        # 2) sum that annotation at the group level
        if OrderItem is not None:
            oi = OrderItem.objects.filter(order__in=base)

            line_total = ExpressionWrapper(
                F("qty") * F("unit_price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )

            # Group: Items
            top_items = (
                oi.annotate(line_total=line_total)
                  .values("item__name")
                  .annotate(
                      total_qty=Sum("qty"),
                      sales=Sum("line_total"),
                  )
                  .order_by("-total_qty")[:10]
            )

            # Group: Categories
            top_categories = (
                oi.annotate(line_total=line_total)
                  .values("item__category")
                  .annotate(
                      total_qty=Sum("qty"),
                      sales=Sum("line_total"),
                  )
                  .order_by("-sales")[:8]
            )
        else:
            top_items = []
            top_categories = []

        ctx.update({
            "kpis": {"revenue": revenue, "orders": orders, "users": users, "aov": aov},
            "by_day": list(by_day),
            "top_items": list(top_items),
            "top_categories": list(top_categories),
        })

    return render(request, "admin/analytics.html", ctx)
