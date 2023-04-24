from functools import partial
from pathlib import Path

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.api_v0.api import api_router as api_router_v0
from app.core.settings import settings
from app.custom_logging import CustomizeLogger
from app.schemas.response import Error, ErrorResponse, Status, ValidationErrorResponse
from app.signals import *  # noqa # pylint: disable=wildcard-import

if settings.SENTRY.DSN is not None:
    sentry_sdk.init(settings.SENTRY.DSN, environment=settings.SENTRY.ENVIRONMENT)


async def startup(app: FastAPI) -> None:  # pylint: disable=unused-argument,redefined-outer-name
    pass


async def shutdown(app: FastAPI) -> None:  # pylint: disable=unused-argument,redefined-outer-name
    pass


def create_app() -> FastAPI:
    app = FastAPI(  # pylint: disable=redefined-outer-name
        title=settings.APP.NAME,
        version=settings.APP.VERSION,
        openapi_url=f"{settings.APP.PREFIX}/openapi.json",
        docs_url=f"{settings.APP.PREFIX}/docs",
        redoc_url=f"{settings.APP.PREFIX}/redoc",
        swagger_ui_oauth2_redirect_url=f"{settings.APP.PREFIX}/docs/oauth2-redirect",
    )
    logger = CustomizeLogger.make_logger(Path(__file__).with_name("api_logging.json"))
    app.logger = logger  # type: ignore
    return app


app = create_app()

app.add_event_handler(event_type="startup", func=partial(startup, app=app))
app.add_event_handler(event_type="shutdown", func=partial(shutdown, app=app))
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.APP.SECRET_KEY, https_only=True)


async def validation_exception_handler(  # pylint: disable=unused-argument
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    # Exception
    # Override request validation exceptions
    return JSONResponse(
        content=ValidationErrorResponse(
            status=Status.error,
            error=Error(code=status.HTTP_400_BAD_REQUEST, message=exc.errors()),
            data=None,
        ).dict(),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


app.add_exception_handler(RequestValidationError, validation_exception_handler)


# Override the HTTPException error handler
async def http_exception_handler(  # pylint: disable=unused-argument
    request: Request, exc: HTTPException
) -> JSONResponse:
    return JSONResponse(
        content=ErrorResponse(
            status=Status.error,
            error=Error(code=exc.status_code, message=str(exc.detail)),
            data=None,
        ).dict(),
        status_code=exc.status_code,
    )


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(api_router_v0, prefix=f"{settings.APP.PREFIX}/api/v0")
