"""
ASGI config for libre_lims project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from pathlib import Path

from django.core.asgi import get_asgi_application

# Load environment variables from .env file if dotenv is available
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "libre_lims.settings")

application = get_asgi_application()
