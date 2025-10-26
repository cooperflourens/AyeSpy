import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import search as search_router
from .routers import reps as reps_router
from .routers import bills as bills_router
from .routers import chat as chat_router


def create_app() -> FastAPI:
    app = FastAPI(title="AyeSpy v2", version="0.1.0")

    # Static and templates
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    templates_dir = os.path.join(base_dir, "templates")

    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    templates = Jinja2Templates(directory=templates_dir)

    # Routers
    app.include_router(search_router.router)
    app.include_router(reps_router.router)
    app.include_router(bills_router.router)
    app.include_router(chat_router.router)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()


