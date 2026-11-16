import hashlib
import hmac
import json
import time

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import Client
from mercypay import MercyPay

from mercypay_django import get_client, webhook_received

SECRET = "whsec_test"
PAYLOAD = json.dumps({"id": "evt_1", "object": "event", "type": "payment.succeeded", "data": {"id": "pay_1", "metadata": {"order_id": "4821"}}})


def post(payload=PAYLOAD, timestamp=None, secret=SECRET):
    timestamp = timestamp or int(time.time())
    signature = hmac.new(secret.encode(), f"{timestamp}.{payload}".encode(), hashlib.sha256).hexdigest()
    return Client(enforce_csrf_checks=True).post("/webhooks/mercy-pay/", payload, content_type="application/json", HTTP_MERCYPAY_SIGNATURE=f"t={timestamp},v1={signature}")


@pytest.fixture
def received():
    events = []

    def receiver(sender, event, event_type, **kwargs):
        events.append((event_type, event))

    webhook_received.connect(receiver)
    yield events
    webhook_received.disconnect(receiver)


def test_a_signed_webhook_sends_the_signal(received):
    response = post()

    assert response.status_code == 200
    assert received[0][0] == "payment.succeeded"
    assert received[0][1].data.metadata["order_id"] == "4821"


def test_a_bad_or_old_signature_is_refused(received):
    assert post(secret="whsec_other").status_code == 400
    assert post(timestamp=int(time.time()) - 600).status_code == 400
    assert Client().post("/webhooks/mercy-pay/", PAYLOAD, content_type="application/json").status_code == 400
    assert Client().get("/webhooks/mercy-pay/").status_code == 405
    assert received == []


def test_a_failing_receiver_makes_the_event_come_again(settings):
    def broken(sender, **kwargs):
        raise RuntimeError("base indisponible")

    webhook_received.connect(broken)
    try:
        with pytest.raises(RuntimeError):
            post()
    finally:
        webhook_received.disconnect(broken)


def test_a_missing_secret_is_a_500(settings):
    settings.MERCY_PAY = {"API_KEY": "mp_sandbox_test"}
    assert post().status_code == 500


def test_the_client_comes_from_the_settings(settings):
    get_client.cache_clear()
    assert isinstance(get_client(), MercyPay)

    get_client.cache_clear()
    settings.MERCY_PAY = {}
    with pytest.raises(ImproperlyConfigured):
        get_client()
    get_client.cache_clear()
