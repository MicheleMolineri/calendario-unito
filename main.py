#!/usr/bin/env python3
"""
WSGI entry point per Railway
"""

from app import app

# Non chiamare app.run() quando usato con Gunicorn
# Gunicorn gestisce il server WSGI direttamente