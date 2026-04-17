"""
Vercel serverless entry-point.
Vercel's Python runtime looks for an ASGI/WSGI `app` in this file.
We simply re-export the Flask application from the project root.
"""
import sys
import os

# Make sure the project root is on sys.path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app  # noqa: F401  – Vercel picks up `app` automatically
