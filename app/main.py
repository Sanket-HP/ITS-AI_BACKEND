from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.system import router as system_router
from app.core.config import settings, validate_settings


# Validate critical environment variables at startup
validate_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI system architect powered by Gemini 3",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# --------------------------------------------------
# CORS (required for frontend integration)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon-safe; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Routers
# --------------------------------------------------
app.include_router(system_router, prefix=settings.API_PREFIX)


# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.get("/", summary="Health check")
def health():
    return {
        "status": "backend running",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
