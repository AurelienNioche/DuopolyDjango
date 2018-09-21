"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adminbase.settings")
os.environ.setdefault("ASGI_THREADS", "9")
django.setup()
application = get_default_application()