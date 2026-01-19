"""
Vercel serverless function entry point for Flask API.

This file is the entry point for Vercel's Python runtime.
It imports and exposes the Flask app for serverless execution.
"""
import os
import sys

# Add the parent directory to Python path so we can import from app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create app with production config
app = create_app('production')

# Vercel expects the app to be named 'app' or 'handler'
# The Flask app itself serves as the WSGI handler
