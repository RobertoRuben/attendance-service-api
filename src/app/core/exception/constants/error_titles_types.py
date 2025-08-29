class ErrorTitles:
    """
    Generic titles for error types according to RFC 7807.
    These should be reusable for the same HTTP status codes.
    """

    # 4xx Client Errors
    BAD_REQUEST = "Bad Request"
    UNAUTHORIZED = "Unauthorized"
    FORBIDDEN = "Forbidden"
    NOT_FOUND = "Not Found"
    CONFLICT = "Conflict"
    UNPROCESSABLE_ENTITY = "Unprocessable Entity"

    # 5xx Server Errors
    INTERNAL_SERVER_ERROR = "Internal Server Error"
    DATABASE_ERROR = "Database Error"
    IMPLEMENTATION_ERROR = "Implementation Error"
