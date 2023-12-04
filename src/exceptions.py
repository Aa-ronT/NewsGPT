class GoogleApiError(Exception):
    """Exception for Google API related errors."""
    def __init__(self, message: str = "An error occurred with Google's API"):
        super().__init__(message)

class OpenAiApiError(Exception):
    """Exception for OpenAI API related errors."""
    def __init__(self, message: str = "An error occurred with OpenAI's API"):
        super().__init__(message)

class HttpsError(Exception):
    """Custom exception for HTTPS request errors."""
    def __init__(self, message: str = "An error occured with the Https request"):
        super().__init__(message)
