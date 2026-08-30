from fastapi import APIRouter, status

from app.api.deps import AuthSvc
from app.schemas.common import Response, ok
from app.schemas.token import RefreshRequest, TokenPair
from app.schemas.user import UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: UserCreate, svc: AuthSvc) -> dict:
    user = await svc.register(payload)
    return ok(UserRead.model_validate(user))


@router.post("/login", response_model=Response[TokenPair])
async def login(payload: UserLogin, svc: AuthSvc) -> dict:
    tokens = await svc.login(payload)
    return ok(tokens)


@router.post("/refresh", response_model=Response[TokenPair])
async def refresh(payload: RefreshRequest, svc: AuthSvc) -> dict:
    tokens = await svc.refresh(payload.refresh_token)
    return ok(tokens)
