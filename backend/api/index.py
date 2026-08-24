import sys
from pathlib import Path

# Resolve backend directory and add to sys.path for Vercel serverless environment
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

# Export app for Vercel ASGI serverless handler
__all__ = ["app"]
