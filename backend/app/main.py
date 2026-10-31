from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import init_db

# Import all routers
from backend.app.routers import (
    dashboard,
    skus,
    locations,
    demand,
    inventory,
    suppliers,
    purchase_orders,
    production,
    shortages,
    mitigations,
    validation,
    data_generation,
    exports,
    exceptions,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="End-to-End Inventory & Supply Chain Demand Planning System with explainable shortage detection, multi-strategy mitigation, and automated validation."
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "timestamp": "2026-10-31T12:00:00Z"}

# Register API Routers
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
app.include_router(skus.router, prefix=settings.API_PREFIX)
app.include_router(locations.router, prefix=settings.API_PREFIX)
app.include_router(demand.router, prefix=settings.API_PREFIX)
app.include_router(inventory.router, prefix=settings.API_PREFIX)
app.include_router(suppliers.router, prefix=settings.API_PREFIX)
app.include_router(purchase_orders.router, prefix=settings.API_PREFIX)
app.include_router(production.router, prefix=settings.API_PREFIX)
app.include_router(shortages.router, prefix=settings.API_PREFIX)
app.include_router(mitigations.router, prefix=settings.API_PREFIX)
app.include_router(validation.router, prefix=settings.API_PREFIX)
app.include_router(data_generation.router, prefix=settings.API_PREFIX)
app.include_router(exports.router, prefix=settings.API_PREFIX)
app.include_router(exceptions.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
