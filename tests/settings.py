SECRET_KEY = "tests"
INSTALLED_APPS = ["django.contrib.contenttypes", "mercypay_django"]
ROOT_URLCONF = "tests.urls"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
MERCY_PAY = {"API_KEY": "mp_sandbox_test", "WEBHOOK_SECRET": "whsec_test"}
USE_TZ = True
