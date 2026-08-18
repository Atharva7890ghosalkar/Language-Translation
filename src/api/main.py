from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.model_service import DEVICE
from src.api.schemas import HealthResponse
from src.api.routes.translation import router as translation_router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Multilingual Language Translation API",
    description="Multilingual translation API using NLLB-200 on GPU",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(translation_router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Return service health status and active hardware device."""
    return HealthResponse(
        status="ok",
        service="Language Translation API",
        device=DEVICE
    )


# Mount static assets directory
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the single-page application frontend index.html."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "status": "ok",
        "service": "Language Translation API",
        "device": DEVICE,
        "message": "Frontend index.html not found under static directory."
    }
