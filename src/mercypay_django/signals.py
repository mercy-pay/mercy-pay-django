from django.dispatch import Signal

#: Sent for every verified webhook, with ``event`` (the event, fields readable as attributes)
#: and ``event_type`` ("payment.succeeded"…). A receiver that raises makes the view answer 500,
#: so Mercy Pay sends the event again later.
webhook_received = Signal()
