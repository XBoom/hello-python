from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, SuperUser, UserSvc
from app.schemas.common import PageResult, Response, ok
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=Response[UserRead])
async def read_me(current_user: CurrentUser) -> dict:
    return ok(UserRead.model_validate(current_user))


@router.patch("/me", response_model=Response[UserRead])
async def update_me(
    payload: UserUpdate,
    current_user: CurrentUser,
    svc: UserSvc,
) -> dict:
    payload.is_active = None
    user = await svc.update(current_user.id, payload)
    return ok(UserRead.model_validate(user))


@router.get("", response_model=Response[PageResult[UserRead]])
async def list_users(
    _superuser: SuperUser,
    svc: UserSvc,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    items, total = await svc.list_users(
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return ok(
        PageResult[UserRead](
            items=[UserRead.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/{user_id}", response_model=Response[UserRead])
async def get_user(
    user_id: UUID,
    _superuser: SuperUser,
    svc: UserSvc,
) -> dict:
    user = await svc.get(user_id)
    return ok(UserRead.model_validate(user))
