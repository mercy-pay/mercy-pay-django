# Mercy Pay pour Django

[Mercy Pay](https://mercy-pay.com) dans un projet Django 4.2 ou plus : un client configuré par vos settings, et une vue qui reçoit les webhooks, vérifie leur signature et envoie un signal.

```sh
pip install mercy-pay-django
```

## Configurer

```python
# settings.py
INSTALLED_APPS = [..., "mercypay_django"]

MERCY_PAY = {
    "API_KEY": env("MERCY_PAY_API_KEY"),            # mp_sandbox_… ou mp_live_…
    "WEBHOOK_SECRET": env("MERCY_PAY_WEBHOOK_SECRET"),  # whsec_…
}
```

Sans `MERCY_PAY`, les variables d'environnement `MERCY_PAY_API_KEY` et `MERCY_PAY_WEBHOOK_SECRET` sont lues.

```python
# urls.py
urlpatterns = [
    path("webhooks/mercy-pay/", include("mercypay_django.urls")),
]
```

## Encaisser un paiement

```python
from django.shortcuts import redirect
from mercypay_django import get_client

def pay(request, order_id):
    order = Order.objects.get(pk=order_id, customer=request.user)
    session = get_client().checkout_sessions.create(
        amount=order.total,
        currency="XAF",
        success_url=request.build_absolute_uri(order.get_absolute_url()),
        metadata={"order_id": str(order.pk)},
        idempotency_key=f"order-{order.pk}",
    )
    return redirect(session.checkout_url)
```

`get_client()` renvoie le client [`mercy-pay`](https://github.com/mercy-pay/mercy-pay-python), avec toutes ses méthodes.

## Recevoir les webhooks

Déclarez `https://votre-site/webhooks/mercy-pay/` comme endpoint dans Développeurs > Webhooks, puis écoutez le signal :

```python
# orders/receivers.py, importé dans OrdersConfig.ready()
from django.dispatch import receiver
from mercypay_django import webhook_received

@receiver(webhook_received)
def on_mercy_pay_event(sender, event, event_type, **kwargs):
    if event_type == "payment.succeeded":
        Order.objects.filter(pk=event.data.metadata["order_id"]).update(status="paid")
```

- Une mauvaise signature reçoit un `400`, et le signal n'est pas envoyé. La vue est exemptée de CSRF.
- Si un receveur lève une erreur, la vue répond `500` : Mercy Pay renverra l'événement plus tard.
- Un même événement peut arriver deux fois : servez-vous de `event.id`.
- Pour un travail long, passez-le à Celery ou à une autre file depuis le receveur.

## En local

```sh
mercypay listen --forward-to localhost:8000/webhooks/mercy-pay/
mercypay trigger payment.succeeded
```

La [CLI](https://docs.mercy-pay.com/developers/cli) affiche son secret de signature au démarrage : mettez-le dans `MERCY_PAY_WEBHOOK_SECRET` en local.
