import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.cache import get_cache
from app.core.config import settings
from app.core.constants import ErrorCode
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.db.session import engine

logger = logging.getLogger(__name__)

OPENAPI_TAGS: list[dict[str, str]] = [
    {"name": "auth", "description": "登录/注册/刷新令牌"},
    {"name": "users", "description": "用户管理"},
    {"name": "health", "description": "健康/就绪检查"},
]


def custom_openapi() -> dict[str, Any]:
    """自定义 OpenAPI schema：注入 BearerAuth 安全定义。

    返回值会被 FastAPI 缓存（绑定到 app.openapi_schema），避免每次请求都重建。
    """
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        contact=app.contact,
        license_info=app.license_info,
        tags=app.openapi_tags,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})[
        "BearerAuth"
    ] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    app.openapi_schema = schema
    return schema


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    # 启动期探测 Redis 连通性(若配置)。失败仅 WARN,不阻断启动。
    cache = get_cache()
    if settings.REDIS_URL:
        if await cache.ping():
            logger.info("Redis 缓存连通性 OK url=%s", settings.REDIS_URL)
        else:
            logger.warning("Redis 缓存连通性失败 url=%s,降级为缓存层自处理", settings.REDIS_URL)
    yield
    await cache.close()
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.APP_NAME} - {settings.ENVIRONMENT}",
        version=settings.APP_VERSION,
        description="FastAPI 后端服务",
        debug=settings.DEBUG,
        lifespan=lifespan,
        contact={"name": "Backend Team"},
        license_info={"name": "MIT"},
        openapi_tags=OPENAPI_TAGS,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )

    app.openapi = custom_openapi  # type: ignore[method-assign]

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "请求参数校验失败",
                "data": exc.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code * 100 + 1,
                "message": exc.detail if isinstance(exc.detail, str) else "请求失败",
                "data": None,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("未处理异常: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.INTERNAL,
                "message": "服务器内部错误",
                "data": {"detail": str(exc)} if settings.DEBUG else None,
            },
        )

    return app


app = create_app()