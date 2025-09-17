from typing import List, Dict, Any


def extract_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract and format Pydantic validation errors in a consistent manner.

    This function processes raw Pydantic validation errors and extracts custom error messages
    from field validators while maintaining compatibility with standard validation errors.
    It handles both built-in Pydantic validation errors and custom ValueError exceptions
    raised by field validators.

    Args:
        errors: List of raw validation error dictionaries from Pydantic containing
               error details such as location, message, type, and context.

    Returns:
        A list of formatted validation error dictionaries, each containing:
        - field: Clean field path without internal prefixes
        - message: User-friendly error message (custom when available)
        - type: Validation error type identifier
        - input: The input value that caused the validation error

    Note:
        Custom ValueError messages are extracted from the "Value error, {message}" format
        that Pydantic uses to wrap custom field validator exceptions.

    Examples:
        >>> errors = [
        ...     {
        ...         "loc": ("body", "email"),
        ...         "msg": "Value error, Invalid email format",
        ...         "type": "value_error",
        ...         "input": "invalid-email"
        ...     }
        ... ]
        >>> result = extract_validation_errors(errors)
        >>> result[0]["field"]
        'email'
        >>> result[0]["message"]
        'Invalid email format'
    """
    validation_errors = []

    for error in errors:
        # Extract basic error information from Pydantic error structure
        field_path = " -> ".join(str(loc) for loc in error.get("loc", []))
        error_msg = error.get("msg", "Validation error")
        error_type = error.get("type", "validation_error")
        error_input = error.get("input")

        # Clean field path by removing internal Pydantic prefixes
        clean_field_path = field_path.replace("body -> ", "")

        # Handle custom validation errors from field_validator decorators
        if error_type == "value_error":
            # Extract custom message from Pydantic's "Value error, {custom_message}" format
            if error_msg.startswith("Value error, "):
                custom_message = error_msg[13:]  # Remove "Value error, " prefix
                if custom_message:
                    error_msg = custom_message

            # Check context for additional error information from validator functions
            ctx = error.get("ctx", {})
            if "error" in ctx:
                context_error = ctx["error"]
                if isinstance(context_error, Exception):
                    error_msg = str(context_error)

        validation_errors.append(
            {
                "field": clean_field_path,
                "message": error_msg,
                "type": error_type,
                "input": error_input,
            }
        )

    return validation_errors


def format_validation_response_details(
    validation_errors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Format validation errors into a standardized response structure.

    Args:
        validation_errors: List of formatted validation errors from extract_validation_errors.

    Returns:
        A dictionary containing formatted validation error details ready for API responses.

    Examples:
        >>> errors = [{"field": "email", "message": "Invalid format", "type": "value_error", "input": "test"}]
        >>> result = format_validation_response_details(errors)
        >>> result["total_errors"]
        1
        >>> result["message"]
        'Please correct the highlighted errors and try again'
    """
    return {
        "validation_errors": validation_errors,
        "total_errors": len(validation_errors),
        "message": "Please correct the highlighted errors and try again",
    }
