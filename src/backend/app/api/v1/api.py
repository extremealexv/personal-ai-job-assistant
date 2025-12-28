"""API v1 router and endpoint aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import health

# Create main v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# TODO: Add more routers as they are implemented
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
# api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
