"""
Custom exceptions for the Zeebee AI Python SDK.
"""

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass

class AgentException(Exception):
    """Raised when there is an error with agent operations."""
    pass

class PipelineException(Exception):
    """Raised when there is an error with pipeline operations."""
    pass
