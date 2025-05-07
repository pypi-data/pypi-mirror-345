from typing import TYPE_CHECKING

from archipy.models.dtos.error_dto import ErrorDetailDTO
from archipy.models.types.error_message_types import ErrorMessageType
from archipy.models.types.language_type import LanguageType

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


class BaseError(Exception):
    """Base exception class for all custom errors.

    This class provides a standardized way to handle errors with support for localization,
    additional context data, and integration with HTTP and gRPC status codes.
    """

    def __init__(
        self,
        error: ErrorDetailDTO | ErrorMessageType | None = None,
        lang: LanguageType = LanguageType.FA,
        additional_data: dict | None = None,
        *args: object,
    ) -> None:
        """Initializes the base exception.

        Args:
            error: The error detail or message. Can be:
                - ErrorDetail: Direct error detail object
                - ExceptionMessageType: Enum member containing error detail
                - None: Will use UNKNOWN_ERROR
            lang: Language code for the error message (defaults to Persian).
            additional_data: Additional context data for the error.
            *args: Additional arguments for the base Exception class.
        """
        if isinstance(error, ErrorMessageType):
            self.error_detail = error.value
        elif isinstance(error, ErrorDetailDTO):
            self.error_detail = error
        else:
            self.error_detail = ErrorMessageType.UNKNOWN_ERROR.value

        self.lang = lang
        self.additional_data = additional_data or {}

        # Initialize base Exception with the message
        super().__init__(self.get_message(), *args)

    def get_message(self) -> str:
        """Gets the localized error message based on the language setting.

        Returns:
            str: The error message in the current language.
        """
        return self.error_detail.message_fa if self.lang == LanguageType.FA else self.error_detail.message_en

    def to_dict(self) -> dict:
        """Converts the exception to a dictionary format for API responses.

        Returns:
            dict: A dictionary containing error details and additional data.
        """
        response = {
            "error": self.error_detail.code,
            "detail": self.error_detail.model_dump(mode="json", exclude_none=True),
        }

        # Add additional data if present
        detail = response["detail"]
        if isinstance(detail, dict) and self.additional_data:
            detail.update(self.additional_data)

        return response

    @property
    def http_status_code(self) -> int | None:
        """Gets the HTTP status code if HTTP support is available.

        Returns:
            Optional[int]: The HTTP status code or None if HTTP is not available.
        """
        return self.error_detail.http_status if HTTP_AVAILABLE else None

    @property
    def grpc_status_code(self) -> int | None:
        """Gets the gRPC status code if gRPC support is available.

        Returns:
            Optional[int]: The gRPC status code or None if gRPC is not available.
        """
        return self.error_detail.grpc_status if GRPC_AVAILABLE else None

    def __str__(self) -> str:
        """String representation of the exception.

        Returns:
            str: A formatted string containing the error code and message.
        """
        return f"[{self.error_detail.code}] {self.get_message()}"

    def __repr__(self) -> str:
        """Detailed string representation of the exception.

        Returns:
            str: A detailed string representation including all error details.
        """
        return (
            f"{self.__class__.__name__}("
            f"code='{self.error_detail.code}', "
            f"message='{self.get_message()}', "
            f"http_status={self.http_status_code}, "
            f"grpc_status={self.grpc_status_code}, "
            f"additional_data={self.additional_data}"
            f")"
        )

    @property
    def code(self) -> str:
        """Gets the error code.

        Returns:
            str: The error code.
        """
        return self.error_detail.code

    @property
    def message(self) -> str:
        """Gets the current language message.

        Returns:
            str: The error message in the current language.
        """
        return self.get_message()

    @property
    def message_en(self) -> str:
        """Gets the English message.

        Returns:
            str: The English error message.
        """
        return self.error_detail.message_en

    @property
    def message_fa(self) -> str:
        """Gets the Persian message.

        Returns:
            str: The Persian error message.
        """
        return self.error_detail.message_fa


# Authentication Exceptions
class InvalidPhoneNumberError(BaseError):
    """Exception raised for invalid phone numbers."""

    def __init__(
        self,
        phone_number: str,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INVALID_PHONE.value,
    ) -> None:
        """Initializes the exception.

        Args:
            phone_number: The invalid phone number.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"phone_number": phone_number})


class InvalidLandlineNumberError(BaseError):
    """Exception raised for invalid landline numbers."""

    def __init__(
        self,
        landline_number: str,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INVALID_LANDLINE.value,
    ) -> None:
        """Initializes the exception.

        Args:
            landline_number: The invalid landline number.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"landline_number": landline_number})


class TokenExpiredError(BaseError):
    """Exception raised when a token has expired."""

    def __init__(
        self,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.TOKEN_EXPIRED.value,
    ) -> None:
        """Initializes the exception.

        Args:
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang)


class InvalidTokenError(BaseError):
    """Exception raised when a token is invalid."""

    def __init__(
        self,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INVALID_TOKEN.value,
    ) -> None:
        """Initializes the exception.

        Args:
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang)


class PermissionDeniedError(BaseError):
    """Exception raised when permission is denied."""

    def __init__(
        self,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.PERMISSION_DENIED.value,
        additional_data: dict | None = None,
    ) -> None:
        """Initializes the exception.

        Args:
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
            additional_data: Additional context data for the error.
        """
        super().__init__(error, lang, additional_data)


# Resource Error
class NotFoundError(BaseError):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        resource_type: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.NOT_FOUND.value,
    ) -> None:
        """Initializes the exception.

        Args:
            resource_type: The type of resource that was not found.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"resource_type": resource_type} if resource_type else None)


class AlreadyExistsError(BaseError):
    """Exception raised when a resource already exists."""

    def __init__(
        self,
        resource_type: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.ALREADY_EXISTS.value,
    ) -> None:
        """Initializes the exception.

        Args:
            resource_type: The type of resource that already exists.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"resource_type": resource_type} if resource_type else None)


# Validation Exceptions
class InvalidArgumentError(BaseError):
    """Exception raised for invalid arguments."""

    def __init__(
        self,
        argument_name: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INVALID_ARGUMENT.value,
    ) -> None:
        """Initializes the exception.

        Args:
            argument_name: The name of the invalid argument.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"argument": argument_name} if argument_name else None)


class OutOfRangeError(BaseError):
    """Exception raised when a value is out of range."""

    def __init__(
        self,
        field_name: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.OUT_OF_RANGE.value,
    ) -> None:
        """Initializes the exception.

        Args:
            field_name: The name of the field that is out of range.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"field": field_name} if field_name else None)


# Operation Exceptions
class DeadlineExceededError(BaseError):
    """Exception raised when a deadline is exceeded."""

    def __init__(
        self,
        operation: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.DEADLINE_EXCEEDED.value,
    ) -> None:
        """Initializes the exception.

        Args:
            operation: The operation that exceeded the deadline.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"operation": operation} if operation else None)


class DeprecationError(BaseError):
    """Exception raised for deprecated operations."""

    def __init__(
        self,
        operation: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.DEPRECATION.value,
    ) -> None:
        """Initializes the exception.

        Args:
            operation: The deprecated operation.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"operation": operation} if operation else None)


class FailedPreconditionError(BaseError):
    """Exception raised when a precondition fails."""

    def __init__(
        self,
        condition: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.FAILED_PRECONDITION.value,
    ) -> None:
        """Initializes the exception.

        Args:
            condition: The failed precondition.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"condition": condition} if condition else None)


class ResourceExhaustedError(BaseError):
    """Exception raised when resources are exhausted."""

    def __init__(
        self,
        resource_type: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.RESOURCE_EXHAUSTED.value,
    ) -> None:
        """Initializes the exception.

        Args:
            resource_type: The type of resource that is exhausted.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"resource_type": resource_type} if resource_type else None)


class AbortedError(BaseError):
    """Exception raised when an operation is aborted."""

    def __init__(
        self,
        reason: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.ABORTED.value,
    ) -> None:
        """Initializes the exception.

        Args:
            reason: The reason for the abort.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"reason": reason} if reason else None)


class CancelledError(BaseError):
    """Exception raised when an operation is cancelled."""

    def __init__(
        self,
        reason: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.CANCELLED.value,
    ) -> None:
        """Initializes the exception.

        Args:
            reason: The reason for the cancellation.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"reason": reason} if reason else None)


# System Exceptions
class InternalError(BaseError):
    """Exception raised for internal errors."""

    def __init__(
        self,
        details: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INTERNAL_ERROR.value,
    ) -> None:
        """Initializes the exception.

        Args:
            details: Additional details about the internal error.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"details": details} if details else None)


class DataLossError(BaseError):
    """Exception raised when data is lost."""

    def __init__(
        self,
        details: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.DATA_LOSS.value,
    ) -> None:
        """Initializes the exception.

        Args:
            details: Additional details about the data loss.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"details": details} if details else None)


class UnImplementedError(BaseError):
    """Exception raised for unimplemented features."""

    def __init__(
        self,
        feature: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.UNIMPLEMENTED.value,
    ) -> None:
        """Initializes the exception.

        Args:
            feature: The unimplemented feature.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"feature": feature} if feature else None)


class UnavailableError(BaseError):
    """Exception raised when a service is unavailable."""

    def __init__(
        self,
        service: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.UNAVAILABLE.value,
    ) -> None:
        """Initializes the exception.

        Args:
            service: The unavailable service.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"service": service} if service else None)


class UnknownError(BaseError):
    """Exception raised for unknown errors."""

    def __init__(
        self,
        details: str | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.UNKNOWN_ERROR.value,
    ) -> None:
        """Initializes the exception.

        Args:
            details: Additional details about the unknown error.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"details": details} if details else None)


class InvalidNationalCodeError(BaseError):
    """Exception raised for invalid national codes."""

    def __init__(
        self,
        national_code: str,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INVALID_NATIONAL_CODE.value,
    ) -> None:
        """Initializes the exception.

        Args:
            national_code: The invalid national code.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"national_code": national_code})


class InvalidEntityTypeError(BaseError):
    """Exception raised for invalid entity types."""

    def __init__(
        self,
        entity_type: object | None = None,
        expected_type: type | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INVALID_ENTITY_TYPE.value,
    ) -> None:
        """Initializes the exception.

        Args:
            entity_type: The invalid entity type.
            expected_type: The expected entity type.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"entity_type": entity_type, "expected_type": expected_type})


class DeadlockDetectedError(BaseError):
    """Exception raised when a deadlock is detected."""

    def __init__(
        self,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.DEADLOCK.value,
    ) -> None:
        """Initializes the exception.

        Args:
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang)


class UnauthenticatedError(BaseError):
    """Exception raised when a user is unauthenticated."""

    def __init__(
        self,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.UNAUTHENTICATED.value,
    ) -> None:
        """Initializes the exception.

        Args:
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang)


class InvalidPasswordError(BaseError):
    """Exception raised when a password does not meet the security requirements."""

    def __init__(
        self,
        requirements: list[str] | None = None,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INVALID_PASSWORD.value,
    ) -> None:
        """Initializes the exception.

        Args:
            requirements: List of specific password requirements that were not met.
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang, additional_data={"requirements": requirements} if requirements else None)


class InsufficientBalanceError(BaseError):
    """Exception raised when an operation fails due to insufficient account balance."""

    def __init__(
        self,
        lang: LanguageType = LanguageType.FA,
        error: ErrorDetailDTO = ErrorMessageType.INSUFFICIENT_BALANCE.value,
    ) -> None:
        """Initializes the exception.

        Args:
            lang: Language code for the error message (defaults to Persian).
            error: The error detail or message.
        """
        super().__init__(error, lang)
