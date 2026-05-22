# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

from menu.models import Item
from .models import Order, OrderItem
from payments.models import Payment
from core.models import SitePayment

# NEW: for server-side QR fallback
import qrcode
from io import BytesIO
import base64


# orders/views.py
def _get_cart(request):
    oid = request.session.get('order_id')
    if oid:
        # fetch regardless of status
        order = Order.objects.filter(id=oid).first()
        if order:
            # If already finalized, start a fresh cart
            if getattr(order, 'status', 'cart') in ('paid', 'completed'):
                pass  # will create new below
            else:
                # If not paid, force it back to 'cart' so items stay intact
                if getattr(order, 'status', 'cart') != 'cart':
                    order.status = 'cart'
                    order.save(update_fields=['status'])
                return order
    # No order or finalized -> create new cart
    order = Order.objects.create(customer_email='')
    request.session['order_id'] = order.id
    return order



def start_order(request):
    order = _get_cart(request)
    if request.method == 'POST':
        email = request.POST.get('email','').strip()
        if not email:
            messages.error(request, 'Please enter email to continue.')
        else:
            order.customer_email = email
            order.recalc_total(); order.save()
            order.status = 'pending'; order.save()
            Payment.objects.get_or_create(order=order, defaults={'amount': order.total})
            return redirect('orders:checkout')
    return render(request, 'orders/cart.html', {'order': order})


@transaction.atomic
def add_to_cart(request, item_id):
    order = _get_cart(request)
    if request.method == 'POST':
        qty = int(request.POST.get('qty', '1') or '1')
        item = get_object_or_404(Item, id=item_id, is_active=True)
        OrderItem.objects.create(order=order, item=item, qty=qty, unit_price=item.price)
        order.recalc_total(); order.save()
        messages.success(request, f'Added {item.name} x{qty}')
    return redirect('menu:today')


from core.models import SitePayment
import qrcode, base64
from io import BytesIO

def _make_qr_b64(data: str) -> str | None:
    try:
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(data); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO(); img.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None

def checkout(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    payment, _ = Payment.objects.get_or_create(order=order, defaults={'amount': order.total})
    if payment.amount != order.total:
        payment.amount = order.total
        payment.save(update_fields=['amount'])

    per_order_url = request.build_absolute_uri(reverse('payments:pay', args=[payment.uuid]))

    site_pay = SitePayment.get_solo()
    qr_img_url = site_pay.qr_image.url if getattr(site_pay, 'qr_image', None) else None
    qr_text = site_pay.payment_link or per_order_url

    qr_b64 = _make_qr_b64(qr_text) if qr_text else None  # fallback that always works

    return render(request, "orders/checkout.html", {
        "order": order,
        "payment": payment,
        "qr_text": qr_text,
        "qr_img_url": qr_img_url,
        "qr_b64": qr_b64,
        "qr_last_updated": getattr(site_pay, "updated_at", None),
    })


def thanks(request, order_id):
    return render(request, 'orders/thanks.html', {'order_id': order_id})

# ── KITCHEN DISPLAY SYSTEM (KDS) ─────────────────────────
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

@staff_member_required
def kds_dashboard(request):
    return render(request, 'orders/kds.html')

@staff_member_required
def kds_api_orders(request):
    """Returns active orders (Paid) that have un-ready items"""
    # Fetch orders that are paid or completed, but have items not 'ready'
    active_orders = Order.objects.filter(status__in=['paid', 'completed'], items__status__in=['pending', 'preparing']).distinct()
    
    data = []
    for order in active_orders.order_by('created_at'):
        items = []
        for item in order.items.all():
            items.append({
                'id': item.id,
                'name': item.item.name,
                'qty': item.qty,
                'status': item.status
            })
        
        # calculate elapsed time in minutes
        delta = timezone.now() - order.created_at
        elapsed_mins = int(delta.total_seconds() / 60)
        
        data.append({
            'id': order.id,
            'table': f"Order #{order.id}", # Can be replaced by table code later
            'elapsed_mins': elapsed_mins,
            'items': items
        })
        
    return JsonResponse({'orders': data})

@staff_member_required
@csrf_exempt # Safe enough for staff internal API, but ideally use standard CSRF
def kds_update_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_status = request.POST.get('status')
        if new_status in dict(OrderItem.STATUS_CHOICES):
            oi = get_object_or_404(OrderItem, id=item_id)
            oi.status = new_status
            if new_status == 'ready':
                oi.prepared_at = timezone.now()
            oi.save()
            return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)

def order_status_api(request, order_id):
    """Customer-facing API to check the real-time prep status of their order."""
    order = get_object_or_404(Order, id=order_id)
    
    items = order.items.all()
    all_ready = items.exists() and all(i.status == 'ready' for i in items)
    any_prep = any(i.status == 'preparing' for i in items)
    
    if all_ready and order.status == 'paid':
        order.status = 'completed'
        order.save(update_fields=['status'])
        
    return JsonResponse({
        'status': order.status,
        'all_ready': all_ready,
        'any_prep': any_prep
    })
