import sys
from pathlib import Path

# Resolve backend directory and add to sys.path for Vercel serverless environment
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = app

__all__ = ["app", "handler"]
