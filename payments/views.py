from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse

from .models import Payment
from core.models import SitePayment


def pay(request, uuid):
    payment = get_object_or_404(Payment, uuid=uuid)
    return render(request, 'payments/pay.html', {'payment': payment})


def payment_status(request, uuid):
    """
    Return JSON with current payment status. Optionally mark as 'initiated'
    the first time the page loads (?init=1). This does NOT redirect anywhere.
    """
    payment = get_object_or_404(Payment, uuid=uuid)

    if request.GET.get("init") == "1" and hasattr(payment, "status"):
        if not payment.status or payment.status in ("new", "created", "pending", "initiated"):
            payment.status = "initiated"
            payment.save(update_fields=["status"])

    data = {
        "status": getattr(payment, "status", "unknown"),
        "amount": float(payment.amount),
        "order_id": payment.order_id,
    }
    return JsonResponse(data)


@staff_member_required
@require_POST
def confirm(request, uuid):
    payment = get_object_or_404(Payment, uuid=uuid)
    order = payment.order

    # Mark payment as confirmed (matches Payment.STATUS choices)
    payment.status = 'confirmed'
    payment.confirmed_at = timezone.now()  # correct field from Payment model
    payment.save(update_fields=['status', 'confirmed_at'])

    # Finalize order
    order.status = 'paid'
    order.recalc_total()
    order.save(update_fields=['status', 'total'])

    # Clear the cart session if this was the active order
    if request.session.get('order_id') == order.id:
        try:
            del request.session['order_id']
        except KeyError:
            pass

    messages.success(request, f"Payment confirmed for Order #{order.id}.")
    return redirect('orders:thanks', order_id=order.id)


@staff_member_required
@require_POST
def mark_failed(request, uuid):
    payment = get_object_or_404(Payment, uuid=uuid)
    order = payment.order

    payment.status = 'failed'
    payment.save(update_fields=['status'])

    # Reopen order so items remain and user can retry
    if getattr(order, 'status', 'cart') != 'paid':
        order.status = 'cart'
        order.save(update_fields=['status'])

    messages.warning(request, f"Payment marked as failed for Order #{order.id}. Order reopened.")
    return redirect('admin:payments_payment_changelist')

@require_POST
def simulate_payment(request, uuid):
    """Dev/Testing bypass to simulate a successful payment without staff login"""
    payment = get_object_or_404(Payment, uuid=uuid)
    order = payment.order

    payment.status = 'confirmed'
    payment.confirmed_at = timezone.now()
    payment.save(update_fields=['status', 'confirmed_at'])

    order.status = 'paid'
    order.recalc_total()
    order.save(update_fields=['status', 'total'])

    if request.session.get('order_id') == order.id:
        try: del request.session['order_id']
        except KeyError: pass

    return JsonResponse({'ok': True})
