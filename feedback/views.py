from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.validators import ValidationError
from .models import Feedback
from orders.models import Order

@require_POST
def submit_feedback(request):
    try:
        rating = int(request.POST.get("rating", "0"))
        comment = (request.POST.get("comment") or "").strip()
        email = (request.POST.get("email") or "").strip()
        order_id = request.POST.get("order_id")

        order = None
        if order_id:
            order = Order.objects.filter(id=order_id).first()

        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be 1–5")

        fb = Feedback.objects.create(rating=rating, comment=comment, email=email, order=order)
        return JsonResponse({"ok": True, "id": fb.id})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)
