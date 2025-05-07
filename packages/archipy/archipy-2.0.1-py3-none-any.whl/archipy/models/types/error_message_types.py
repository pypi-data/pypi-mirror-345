from enum import Enum
from typing import TYPE_CHECKING

from archipy.models.dtos.error_dto import ErrorDetailDTO

try:
    from http import HTTPStatus

    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False
    if not TYPE_CHECKING:
        # Only create at runtime, not during type checking
        HTTPStatus = None

try:
    from grpc import StatusCode

    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False
    if not TYPE_CHECKING:
        # Only create at runtime, not during type checking
        StatusCode = None


class ErrorMessageType(Enum):
    """Enumeration of exception types with associated error details.

    This class defines a set of standard exception types, each with an associated error code,
    English and Farsi messages, and corresponding HTTP and gRPC status codes.

    Attributes:
        UNAUTHENTICATED: Indicates that the user is not authenticated.
        INVALID_PHONE: Indicates an invalid Iranian phone number.
        INVALID_LANDLINE: Indicates an invalid Iranian landline number.
        INVALID_NATIONAL_CODE: Indicates an invalid national code format.
        TOKEN_EXPIRED: Indicates that the authentication token has expired.
        INVALID_TOKEN: Indicates an invalid authentication token.
        PERMISSION_DENIED: Indicates that the user does not have permission for the operation.
        NOT_FOUND: Indicates that the requested resource was not found.
        ALREADY_EXISTS: Indicates that the resource already exists.
        INVALID_ARGUMENT: Indicates an invalid argument was provided.
        OUT_OF_RANGE: Indicates that a value is out of the acceptable range.
        DEADLINE_EXCEEDED: Indicates that the operation deadline was exceeded.
        FAILED_PRECONDITION: Indicates that the operation preconditions were not met.
        RESOURCE_EXHAUSTED: Indicates that the resource limit has been reached.
        ABORTED: Indicates that the operation was aborted.
        CANCELLED: Indicates that the operation was cancelled.
        INVALID_ENTITY_TYPE: Indicates an invalid entity type.
        INTERNAL_ERROR: Indicates an internal system error.
        DATA_LOSS: Indicates critical data loss.
        UNIMPLEMENTED: Indicates that the operation is not implemented.
        DEPRECATION: Indicates that the operation is deprecated.
        UNAVAILABLE: Indicates that the service is unavailable.
        UNKNOWN_ERROR: Indicates an unknown error occurred.
        DEADLOCK: Indicates a deadlock condition was detected.
    """

    # Authentication Errors (400, 401, 403)
    UNAUTHENTICATED = ErrorDetailDTO.create_error_detail(
        code="UNAUTHENTICATED_TYPE",
        message_en="You are not authorized to perform this action.",
        message_fa="شما مجوز انجام این عمل را ندارید.",
        http_status=HTTPStatus.UNAUTHORIZED if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.UNAUTHENTICATED if GRPC_AVAILABLE else None,
    )
    INVALID_PHONE = ErrorDetailDTO.create_error_detail(
        code="INVALID_PHONE",
        message_en="Invalid Iranian phone number",
        message_fa="شماره تلفن همراه ایران نامعتبر است.",
        http_status=HTTPStatus.BAD_REQUEST if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.INVALID_ARGUMENT if GRPC_AVAILABLE else None,
    )

    INVALID_LANDLINE = ErrorDetailDTO.create_error_detail(
        code="INVALID_LANDLINE",
        message_en="Invalid Iranian landline number",
        message_fa="شماره تلفن ثابت ایران نامعتبر است.",
        http_status=HTTPStatus.BAD_REQUEST if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.INVALID_ARGUMENT if GRPC_AVAILABLE else None,
    )

    INVALID_NATIONAL_CODE = ErrorDetailDTO.create_error_detail(
        code="INVALID_NATIONAL_CODE",
        message_en="Invalid national code format",
        message_fa="فرمت کد ملی وارد شده اشتباه است.",
        http_status=HTTPStatus.BAD_REQUEST if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.INVALID_ARGUMENT if GRPC_AVAILABLE else None,
    )

    TOKEN_EXPIRED = ErrorDetailDTO.create_error_detail(
        code="TOKEN_EXPIRED",
        message_en="Authentication token has expired",
        message_fa="توکن احراز هویت منقضی شده است.",
        http_status=HTTPStatus.UNAUTHORIZED if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.UNAUTHENTICATED if GRPC_AVAILABLE else None,
    )

    INVALID_TOKEN = ErrorDetailDTO.create_error_detail(
        code="INVALID_TOKEN",
        message_en="Invalid authentication token",
        message_fa="توکن احراز هویت نامعتبر است.",
        http_status=HTTPStatus.UNAUTHORIZED if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.UNAUTHENTICATED if GRPC_AVAILABLE else None,
    )

    PERMISSION_DENIED = ErrorDetailDTO.create_error_detail(
        code="PERMISSION_DENIED",
        message_en="Permission denied for this operation",
        message_fa="دسترسی برای انجام این عملیات وجود ندارد.",
        http_status=HTTPStatus.FORBIDDEN if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.PERMISSION_DENIED if GRPC_AVAILABLE else None,
    )

    # Resource Errors (404, 409)
    NOT_FOUND = ErrorDetailDTO.create_error_detail(
        code="NOT_FOUND",
        message_en="Requested resource not found",
        message_fa="منبع درخواستی یافت نشد.",
        http_status=HTTPStatus.NOT_FOUND if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.NOT_FOUND if GRPC_AVAILABLE else None,
    )

    ALREADY_EXISTS = ErrorDetailDTO.create_error_detail(
        code="ALREADY_EXISTS",
        message_en="Resource already exists",
        message_fa="منبع از قبل موجود است.",
        http_status=HTTPStatus.CONFLICT if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.ALREADY_EXISTS if GRPC_AVAILABLE else None,
    )

    # Validation Errors (400)
    INVALID_ARGUMENT = ErrorDetailDTO.create_error_detail(
        code="INVALID_ARGUMENT",
        message_en="Invalid argument provided",
        message_fa="پارامتر ورودی نامعتبر است.",
        http_status=HTTPStatus.BAD_REQUEST if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.INVALID_ARGUMENT if GRPC_AVAILABLE else None,
    )

    INVALID_PASSWORD = ErrorDetailDTO.create_error_detail(
        code="INVALID_PASSWORD",
        message_en="Password does not meet the security requirements",
        message_fa="رمز عبور الزامات امنیتی را برآورده نمی‌کند.",
        http_status=HTTPStatus.BAD_REQUEST if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.INVALID_ARGUMENT if GRPC_AVAILABLE else None,
    )

    OUT_OF_RANGE = ErrorDetailDTO.create_error_detail(
        code="OUT_OF_RANGE",
        message_en="Value is out of acceptable range",
        message_fa="مقدار خارج از محدوده مجاز است.",
        http_status=HTTPStatus.BAD_REQUEST if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.OUT_OF_RANGE if GRPC_AVAILABLE else None,
    )

    # Operation Errors (408, 409, 412, 429)
    DEADLINE_EXCEEDED = ErrorDetailDTO.create_error_detail(
        code="DEADLINE_EXCEEDED",
        message_en="Operation deadline exceeded",
        message_fa="مهلت انجام عملیات به پایان رسیده است.",
        http_status=HTTPStatus.REQUEST_TIMEOUT if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.DEADLINE_EXCEEDED if GRPC_AVAILABLE else None,
    )

    FAILED_PRECONDITION = ErrorDetailDTO.create_error_detail(
        code="FAILED_PRECONDITION",
        message_en="Operation preconditions not met",
        message_fa="پیش‌نیازهای عملیات برآورده نشده است.",
        http_status=HTTPStatus.PRECONDITION_FAILED if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.FAILED_PRECONDITION if GRPC_AVAILABLE else None,
    )

    RESOURCE_EXHAUSTED = ErrorDetailDTO.create_error_detail(
        code="RESOURCE_EXHAUSTED",
        message_en="Resource limit has been reached",
        message_fa="محدودیت منابع به پایان رسیده است.",
        http_status=HTTPStatus.TOO_MANY_REQUESTS if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.RESOURCE_EXHAUSTED if GRPC_AVAILABLE else None,
    )

    ABORTED = ErrorDetailDTO.create_error_detail(
        code="ABORTED",
        message_en="Operation was aborted",
        message_fa="عملیات متوقف شد.",
        http_status=HTTPStatus.CONFLICT if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.ABORTED if GRPC_AVAILABLE else None,
    )

    CANCELLED = ErrorDetailDTO.create_error_detail(
        code="CANCELLED",
        message_en="Operation was cancelled",
        message_fa="عملیات لغو شد.",
        http_status=HTTPStatus.CONFLICT if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.CANCELLED if GRPC_AVAILABLE else None,
    )

    INSUFFICIENT_BALANCE = ErrorDetailDTO.create_error_detail(
        code="INSUFFICIENT_BALANCE",
        message_en="Insufficient balance for operation",
        message_fa="عدم موجودی کافی برای عملیات.",
        http_status=HTTPStatus.PAYMENT_REQUIRED if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.FAILED_PRECONDITION if GRPC_AVAILABLE else None,
    )

    # System Errors (500, 501, 503)
    INVALID_ENTITY_TYPE = ErrorDetailDTO.create_error_detail(
        code="INVALID_ENTITY",
        message_en="Invalid entity type",
        message_fa="نوع موجودیت نامعتبر است.",
        http_status=HTTPStatus.BAD_REQUEST if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.INVALID_ARGUMENT if GRPC_AVAILABLE else None,
    )
    INTERNAL_ERROR = ErrorDetailDTO.create_error_detail(
        code="INTERNAL_ERROR",
        message_en="Internal system error occurred",
        message_fa="خطای داخلی سیستم رخ داده است.",
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.INTERNAL if GRPC_AVAILABLE else None,
    )

    DATA_LOSS = ErrorDetailDTO.create_error_detail(
        code="DATA_LOSS",
        message_en="Critical data loss detected",
        message_fa="از دست دادن اطلاعات حیاتی تشخیص داده شد.",
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.DATA_LOSS if GRPC_AVAILABLE else None,
    )

    UNIMPLEMENTED = ErrorDetailDTO.create_error_detail(
        code="UNIMPLEMENTED",
        message_en="Requested operation is not implemented",
        message_fa="عملیات درخواستی پیاده‌سازی نشده است.",
        http_status=HTTPStatus.NOT_IMPLEMENTED if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.UNIMPLEMENTED if GRPC_AVAILABLE else None,
    )

    DEPRECATION = ErrorDetailDTO.create_error_detail(
        code="DEPRECATION",
        message_en="This operation is deprecated and will be removed in a future version.",
        message_fa="این عملیات منسوخ شده و در نسخه‌های آینده حذف خواهد شد.",
        http_status=HTTPStatus.GONE if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.UNAVAILABLE if GRPC_AVAILABLE else None,
    )

    UNAVAILABLE = ErrorDetailDTO.create_error_detail(
        code="UNAVAILABLE",
        message_en="Service is currently unavailable",
        message_fa="سرویس در حال حاضر در دسترس نیست.",
        http_status=HTTPStatus.SERVICE_UNAVAILABLE if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.UNAVAILABLE if GRPC_AVAILABLE else None,
    )

    UNKNOWN_ERROR = ErrorDetailDTO.create_error_detail(
        code="UNKNOWN_ERROR",
        message_en="An unknown error occurred",
        message_fa="خطای ناشناخته‌ای رخ داده است.",
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.UNKNOWN if GRPC_AVAILABLE else None,
    )

    DEADLOCK = ErrorDetailDTO.create_error_detail(
        code="DEADLOCK",
        message_en="Deadlock detected",
        message_fa="خطای قفل‌شدگی (Deadlock) تشخیص داده شد.",
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR if HTTP_AVAILABLE else None,
        grpc_status=StatusCode.INTERNAL if GRPC_AVAILABLE else None,
    )
