from fastapi import status

from app.core.constants import ErrorCode


class AppError(Exception):
    """业务异常，由全局处理器转成统一 JSON 响应。"""

    def __init__(
        self,
        code: int,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedError(AppError):
    def __init__(
        self,
        code: int = ErrorCode.UNAUTHORIZED,
        message: str = "未认证",
    ) -> None:
        super().__init__(code, message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppError):
    def __init__(
        self,
        code: int = ErrorCode.FORBIDDEN,
        message: str = "无权限",
    ) -> None:
        super().__init__(code, message, status.HTTP_403_FORBIDDEN)


class NotFoundError(AppError):
    def __init__(
        self,
        code: int = ErrorCode.NOT_FOUND,
        message: str = "资源不存在",
    ) -> None:
        super().__init__(code, message, status.HTTP_404_NOT_FOUND)


class ConflictError(AppError):
    def __init__(
        self,
        code: int = ErrorCode.CONFLICT,
        message: str = "资源冲突",
    ) -> None:
        super().__init__(code, message, status.HTTP_409_CONFLICT)
