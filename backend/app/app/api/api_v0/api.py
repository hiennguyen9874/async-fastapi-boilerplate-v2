from typing import Any

from fastapi import APIRouter

from app.api.api_v0.endpoints import auth, items, tests, users
from app.schemas.response import ErrorResponse, ValidationErrorResponse

api_router = APIRouter(
    responses={
        422: {
            "model": ValidationErrorResponse[str | dict[str, Any]],
            "description": "Validation Error",
        }
    }
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
    responses={
        403: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Incorrect email or password",
        },
        404: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "User not found",
        },
    },
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    responses={
        401: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Could not validate credentials",
        },
        403: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Inactive user or the user doesn't have enough privileges",
        },
        404: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "User not found",
        },
        422: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Username already exists",
        },
    },
)
api_router.include_router(
    items.router,
    prefix="/items",
    tags=["items"],
    responses={
        401: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Could not validate credentials",
        },
        403: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Inactive user or the user doesn't have enough privileges",
        },
        404: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "User not found",
        },
    },
)
api_router.include_router(
    tests.router,
    prefix="/tests",
    tags=["tests"],
    responses={
        401: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Could not validate credentials",
        },
        403: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "Inactive user or the user doesn't have enough privileges",
        },
        404: {
            "model": ErrorResponse[str | dict[str, Any]],
            "description": "User not found",
        },
    },
)
