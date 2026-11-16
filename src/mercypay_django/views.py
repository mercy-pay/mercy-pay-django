import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mercypay import SignatureVerificationError, construct_event

from . import conf
from .signals import webhook_received

logger = logging.getLogger("mercypay_django")


@csrf_exempt
@require_POST
def webhook(request: HttpRequest) -> JsonResponse:
    """Verifies the MercyPay-Signature header against the raw body, sends webhook_received,
    then answers 200. A bad signature gets a 400."""
    secret = conf.webhook_secret()
    if not secret:
        logger.error("Mercy Pay : webhook refusé, MERCY_PAY_WEBHOOK_SECRET est vide.")
        return JsonResponse({"error": "Secret de webhook non configuré."}, status=500)

    try:
        event = construct_event(request.body, request.headers.get("MercyPay-Signature"), secret, tolerance=int(conf.setting("TOLERANCE", 300)))
    except SignatureVerificationError as error:
        return JsonResponse({"error": str(error)}, status=400)

    webhook_received.send(sender=webhook, event=event, event_type=event.get("type"))
    return JsonResponse({"received": True})
