class ConfigurationError(Exception):
    """Raised when there is a configuration error."""

    pass


class IntelligenceAPIError(Exception):
    """Raised when there is an error with the Intelligence API."""

    pass


class IngestionError(Exception):
    """Raised when there is an error during document ingestion."""

    pass


class AgentError(Exception):
    """Base exception for agent-related errors."""

    pass


class AgentConfigurationError(AgentError):
    """Raised when there is an error in agent configuration."""

    pass


class AgentExecutionError(AgentError):
    """Raised when there is an error during agent execution."""

    pass


class AgentFunctionError(AgentError):
    """Raised when there is an error with the agent's function execution."""

    pass


class UnauthorizedError(Exception):
    """Raised when there is an unauthorized error."""

    pass


class BadRequestError(Exception):
    """Raised when there is a bad request error."""

    pass


class ServerPermissionError(Exception):
    """Raised when there is a server permission error."""

    pass


class NotFoundError(Exception):
    """Raised when there is a not found error."""

    pass


class NetworkError(Exception):
    """Raised when there is a network error."""

    pass
