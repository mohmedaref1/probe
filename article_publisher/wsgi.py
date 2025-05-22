"""
WSGI config for article_publisher project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'article_publisher.settings')

application = get_wsgi_application()