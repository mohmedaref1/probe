"""
ASGI config for article_publisher project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'article_publisher.settings')

application = get_asgi_application()