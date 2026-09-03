"""
Vercel Serverless Entry Point for VeriGate AI FastAPI Backend
"""
import sys
import os

# Ensure root directory is in python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel serverless functions look for 'app' ASGI handler
