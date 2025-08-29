import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.file-track")
ERROR_TYPE_BASE_URL = f"{API_BASE_URL}/errors"


class ErrorTypes:
    """
    Constants for error types used in exceptions.
    These types follow the URN format according to the RFC standard for HTTP errors.
    """

    AUTHENTICATION_FAILED = "urn:problem-type:authentication-failed"
    INACTIVE_ACCOUNT = "urn:problem-type:inactive-account"
    INVALID_TOKEN = "urn:problem-type:invalid-token"
    INVALID_REFRESH_TOKEN = "urn:problem-type:invalid-refresh-token"
    USER_NOT_FOUND = "urn:problem-type:user-not-found"
    MISSING_PERMISSION = "urn:problem-type:missing-permission"

    BAD_REQUEST = "urn:problem-type:bad-request"
    NOT_FOUND = "urn:problem-type:not-found"
    CONFLICT = "urn:problem-type:conflict"
    FORBIDDEN = "urn:problem-type:forbidden"
    SERVER_ERROR = "urn:problem-type:server-error"
    DATABASE_ERROR = "urn:problem-type:database-error"
    VALIDATION_ERROR = "urn:problem-type:validation-error"
    IMPLEMENTATION_ERROR = "urn:problem-type:implementation-error"
    INVALID_FIELD = "urn:problem-type:invalid-field"
    HTTP_ERROR = "urn:problem-type:http-error"
