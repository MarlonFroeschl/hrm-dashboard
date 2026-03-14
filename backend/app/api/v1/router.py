from fastapi import APIRouter

from app.api.v1.routes import applicants

api_router = APIRouter()

api_router.include_router(applicants.router, prefix="/applicants", tags=["applicants"])

# Register route modules here as they are built:
# from app.api.v1.routes import auth, employees, recruitment, offboarding
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
# api_router.include_router(recruitment.router, prefix="/recruitment", tags=["recruitment"])
# api_router.include_router(offboarding.router, prefix="/offboarding", tags=["offboarding"])
