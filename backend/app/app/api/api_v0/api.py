from fastapi import APIRouter

from app.api.api_v0.endpoints import auth, items, users, tests

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
