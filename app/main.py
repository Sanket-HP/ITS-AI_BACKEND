from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes.system import router as system_router
from app.core.config import settings, validate_settings


# --------------------------------------------------
# Validate critical environment variables at startup
# --------------------------------------------------
validate_settings()


# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description="AI system architect powered by Gemini",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)


# --------------------------------------------------
# GLOBAL EXCEPTION GUARD (CRITICAL FOR DEMO)
# --------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("[GLOBAL ERROR]", str(exc))

    return JSONResponse(
        status_code=200,  # ⚠️ intentional — frontend must never break
        content={
            "error": "INTERNAL_GUARD_TRIGGERED",
            "message": "The system recovered from an internal error.",
            "path": request.url.path
        }
    )


# --------------------------------------------------
# CORS (required for frontend integration)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon-safe; restrict later
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
