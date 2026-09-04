import importlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from pydantic import BaseModel

from app.core.config import Settings
from app.main import create_app
from app.schemas.common import PageResult, Response
from app.schemas.token import TokenPair
from app.schemas.user import UserRead


def test_openapi_schema_has_security_scheme() -> None:
    """GET /openapi.json 必须包含 components.securitySchemes.BearerAuth。"""
    schema = importlib.import_module("app.main").app.openapi()
    assert "components" in schema
    schemes = schema["components"].get("securitySchemes", {})
    assert "BearerAuth" in schemes, "缺少 BearerAuth 安全定义"
    bearer = schemes["BearerAuth"]
    assert bearer["type"] == "http"
    assert bearer["scheme"] == "bearer"
    assert bearer["bearerFormat"] == "JWT"


def test_openapi_has_tag_metadata() -> None:
    """OpenAPI 顶层应含 auth/users/health 标签描述。"""
    schema = importlib.import_module("app.main").app.openapi()
    tags = schema.get("tags", [])
    tag_names = {t["name"] for t in tags}
    assert {"auth", "users", "health"}.issubset(tag_names)
    auth_tag = next(t for t in tags if t["name"] == "auth")
    assert "登录" in auth_tag["description"] or "注册" in auth_tag["description"]


def test_response_schema_has_example() -> None:
    """Response[T] / PageResult[T] schema 必须含 example 字段。"""
    response_schema = Response[dict].model_json_schema()
    page_schema = PageResult[dict].model_json_schema()
    assert "example" in response_schema, "Response schema 缺少 example"
    assert "example" in page_schema, "PageResult schema 缺少 example"
    assert response_schema["example"]["code"] == 0
    assert page_schema["example"]["page_size"] == 20

    token_schema = TokenPair.model_json_schema()
    assert "example" in token_schema, "TokenPair schema 缺少 example"

    user_read_schema = UserRead.model_json_schema()
    assert "example" in user_read_schema, "UserRead schema 缺少 example"


def test_openapi_disabled_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    """ENVIRONMENT=production 时 docs_url / openapi_url 应为 None。"""
    import app.main as main_mod
    import app.core.config as config_mod

    # 临时把全局 settings 改造成「生产模式」：DEBUG=False、SECRET_KEY 非默认、ENVIRONMENT=production
    monkeypatch.setattr(config_mod.settings, "DEBUG", False, raising=False)
    monkeypatch.setattr(
        config_mod.settings, "SECRET_KEY", "x" * 32, raising=False
    )
    monkeypatch.setattr(
        config_mod.settings, "ENVIRONMENT", "production", raising=False
    )
    # 同步 app.main 模块内 import 的 settings 引用
    monkeypatch.setattr(main_mod, "settings", config_mod.settings)

    prod_app: FastAPI = create_app()
    assert prod_app.docs_url is None
    assert prod_app.redoc_url is None
    assert prod_app.openapi_url is None

    with TestClient(prod_app) as client:
        resp = client.get("/docs")
        assert resp.status_code == 404
        resp = client.get("/openapi.json")
        assert resp.status_code == 404