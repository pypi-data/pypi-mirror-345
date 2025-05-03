# textxgen/exceptions.py


class TextxGenError(Exception):
    """Base exception class for TextxGen package."""

    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = (
            user_message
            or "We're experiencing some issues. Please contact support@pystack.site"
        )
        super().__init__(self.message)


class APIError(TextxGenError):
    """Exception raised for API-related errors."""

    def __init__(self, message: str, status_code: int = None):
        # Map status codes to user-friendly messages
        user_messages = {
            401: "Authentication failed. Please contact us at support@pystack.site",
            403: "Access denied. Please contact us at support@pystack.site",
            404: "The requested resource was not found.",
            429: "Rate limit exceeded. Please try again later or contact support@pystack.site for increased limits.",
            500: "Internal server error. Please try again later.",
            502: "Bad gateway. Please try again later.",
            503: "Service unavailable. Please try again later.",
            504: "Request timeout. Please try again later.",
        }

        # Get user message based on status code
        user_message = user_messages.get(
            status_code,
            "We're experiencing some issues. Please contact support@pystack.site",
        )

        # Add specific messages for common API errors
        if "rate limit" in message.lower():
            user_message = "Server is experiencing high load. Please try again later or contact support@pystack.site for more information."
        elif "quota" in message.lower() or "credit" in message.lower():
            user_message = "TextxGen is facing some issue currently. Please corporate with us or contact support@pystack.site to solve this issue."
        elif "trial" in message.lower():
            user_message = "Unexpected error occurred. Please contact support@pystack.site to tell us about this issue."

        super().__init__(message, user_message)
        self.status_code = status_code


class ModelNotSupportedError(TextxGenError):
    """Exception raised when an unsupported model is requested."""

    def __init__(self, model: str):
        self.model = model
        super().__init__(f"Model '{model}' is not supported.")


class InvalidInputError(TextxGenError):
    """Exception raised for invalid input parameters."""

    def __init__(self, message: str):
        super().__init__(
            message, message
        )  # Use the same message for both technical and user


class ModelError(TextxGenError):
    """Exception raised for model-related errors."""

    def __init__(self, message: str):
        user_message = (
            f"Model error: {message}. Please check the model name and try again."
        )
        super().__init__(message, user_message)


class ConfigurationError(TextxGenError):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str):
        user_message = "Configuration error. Please check your settings and try again."
        super().__init__(message, user_message)


class NetworkError(TextxGenError):
    """Exception raised for network-related errors."""

    def __init__(self, message: str):
        user_message = (
            "Network error. Please check your internet connection and try again."
        )
        super().__init__(message, user_message)


class TimeoutError(TextxGenError):
    """Exception raised for timeout errors."""

    def __init__(self, message: str):
        user_message = "Request timed out. Please try again later."
        super().__init__(message, user_message)


class ValidationError(TextxGenError):
    """Exception raised for validation errors."""

    def __init__(self, message: str):
        super().__init__(
            message, message
        )  # Use the same message for both technical and user
