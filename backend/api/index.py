import sys
from pathlib import Path

# Add backend directory to sys.path for Vercel execution
file_dir = Path(__file__).resolve().parent
for p in [file_dir, file_dir.parent, Path.cwd()]:
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from app.main import app

app = app
