from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from .models import Payment

def pay(request, uuid):
    payment = get_object_or_404(Payment, uuid=uuid)
    return render(request, 'payments/pay.html', {'payment': payment})


# payments/views.py
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST, require_GET

from .models import Payment
from core.models import SitePayment

# payments/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import Payment

def payment_status(request, uuid):
    """
    Return JSON with current payment status. Optionally mark as 'initiated'
    the first time the page loads (?init=1). This does NOT redirect anywhere.
    """
    payment = get_object_or_404(Payment, uuid=uuid)

    # If your Payment has a 'status' field, mark the first contact as initiated
    if request.GET.get("init") == "1" and hasattr(payment, "status"):
        if not payment.status or payment.status in ("new", "created", "pending", "initiated"):
            # don't flip to 'paid' here; that happens in admin confirm/webhook
            payment.status = "initiated"
            # optionally track a timestamp if your model has it
            if hasattr(payment, "updated_at"):
                payment.updated_at = timezone.now()
            payment.save()

    data = {
        "status": getattr(payment, "status", "unknown"),
        "amount": float(payment.amount),
        "order_id": payment.order_id,
        "updated_at": getattr(payment, "updated_at", None) and getattr(payment, "updated_at").isoformat(),
    }
    return JsonResponse(data)


# payments/views.py
@staff_member_required
@require_POST
def confirm(request, uuid):
    payment = get_object_or_404(Payment, uuid=uuid)
    order = payment.order

    # mark payment paid
    if hasattr(payment, 'status'):
        payment.status = 'paid'
    if hasattr(payment, 'paid_at'):
        payment.paid_at = timezone.now()
    payment.save()

    # finalize order
    order.status = 'paid'
    order.recalc_total()
    order.save(update_fields=['status', 'total'])

    # clear only if paid/completed and it's the active cart
    if request.session.get('order_id') == order.id:
        try:
            del request.session['order_id']
        except KeyError:
            pass

    messages.success(request, f"Payment recorded for Order #{order.id}.")
    return redirect('orders:thanks', order_id=order.id)

# payments/views.py
@staff_member_required
@require_POST
def mark_failed(request, uuid):
    payment = get_object_or_404(Payment, uuid=uuid)
    order = payment.order

    if hasattr(payment, 'status'):
        payment.status = 'failed'
        payment.save(update_fields=['status'])

    # Reopen order so items remain and user can retry
    if getattr(order, 'status', 'cart') != 'paid':
        order.status = 'cart'
        order.save(update_fields=['status'])

    messages.warning(request, f"Payment marked as failed for Order #{order.id}. Order reopened.")
    return redirect('admin:payments_payment_changelist')
