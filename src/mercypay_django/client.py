from functools import lru_cache

from django.core.exceptions import ImproperlyConfigured
from mercypay import MercyPay

from . import conf


@lru_cache(maxsize=1)
def get_client() -> MercyPay:
    """The client built from the settings, created once per process."""
    key = conf.api_key()
    if not key:
        raise ImproperlyConfigured("Mercy Pay : ajoutez MERCY_PAY_API_KEY à votre environnement ou MERCY_PAY['API_KEY'] à vos settings.")
    return MercyPay(key, base_url=conf.setting("BASE_URL"), timeout=float(conf.setting("TIMEOUT", 30.0)), max_retries=int(conf.setting("MAX_RETRIES", 2)))
