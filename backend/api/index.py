import sys
import traceback
from pathlib import Path

# Add all candidate paths to sys.path
file_dir = Path(__file__).resolve().parent
for p in [file_dir, file_dir.parent, Path.cwd()]:
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

try:
    from app.main import app
    try:
        from mangum import Mangum
        handler = Mangum(app)
    except ImportError:
        handler = app
except Exception as err:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()
    err_msg = str(err)
    tb_msg = traceback.format_exc()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
    async def catch_all_error(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend Startup Failed",
                "detail": err_msg,
                "traceback": tb_msg
            }
        )
    handler = app

__all__ = ["app", "handler"]
