from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, cast

from rich.console import Console
from rich.panel import Panel

from shadai.core.exceptions import (
    AgentConfigurationError,
    AgentExecutionError,
    AgentFunctionError,
    BadRequestError,
    ConfigurationError,
    IngestionError,
    IntelligenceAPIError,
    NetworkError,
    NotFoundError,
    ServerPermissionError,
    UnauthorizedError,
)

console = Console()

# Define TypeVars for the function return types
T = TypeVar("T")


def handle_errors(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    Decorator for handling session errors with rich output.

    This decorator preserves the return type of the decorated function.

    Args:
        func: The async function to decorate

    Returns:
        A decorated function with the same return type as the original
    """

    ERROR_MESSAGES = {
        IntelligenceAPIError: {
            "title": "API Error",
            "suggestions": [
                "Check your API call parameters",
                "Check your API key",
                "Verify your available balance",
                "Ensure you have network connectivity",
            ],
        },
        ConfigurationError: {
            "title": "Configuration Error",
            "suggestions": [
                "Set INTELLIGENCE_API_KEY environment variable",
                "Check your configuration settings",
            ],
        },
        IngestionError: {
            "title": "Ingestion Error",
            "suggestions": [
                "Verify your input files exist",
                "Check file permissions",
                "Ensure files are in supported format",
            ],
        },
        AgentConfigurationError: {
            "title": "Agent Configuration Error",
            "suggestions": [
                "Check your agent configuration",
            ],
        },
        AgentExecutionError: {
            "title": "Agent Execution Error",
            "suggestions": [
                "Check your agent configuration",
            ],
        },
        AgentFunctionError: {
            "title": "Agent Function Error",
            "suggestions": [
                "Check your agent configuration",
            ],
        },
        BadRequestError: {
            "title": "Bad Request Error",
            "suggestions": [
                "Check your request parameters",
            ],
        },
        UnauthorizedError: {
            "title": "Unauthorized Error",
            "suggestions": [
                "Check your API key",
            ],
        },
        ServerPermissionError: {
            "title": "Server Permission Error",
            "suggestions": [
                "Check server permissions, report to support",
            ],
        },
        NotFoundError: {
            "title": "Not Found Error",
            "suggestions": [
                "Check the id or alias",
            ],
        },
        NetworkError: {
            "title": "Network Error",
            "suggestions": [
                "Check your network connection",
            ],
        },
    }

    async def cleanup_session(instance: Any) -> None:
        """Helper function to cleanup session if needed."""
        if (
            instance
            and hasattr(instance, "_delete")
            and instance._delete
            and func.__name__ != "__aexit__"
            and not getattr(instance, "_session_cleaned_up", False)
            and not getattr(instance, "_cleanup_from_aexit", False)
        ):
            try:
                has_valid_session = (
                    hasattr(instance, "_session_id")
                    and instance._session_id is not None
                ) or (hasattr(instance, "_alias") and instance._alias is not None)

                if not has_valid_session:
                    console.print(
                        "[yellow]⚙️ No valid session ID or alias found, skipping cleanup[/]"
                    )
                    setattr(instance, "_session_cleaned_up", True)
                    return

                if (
                    hasattr(instance, "_cleanup_in_progress")
                    and instance._cleanup_in_progress
                ):
                    console.print(
                        "[yellow]⚙️ Cleanup already in progress, skipping recursive cleanup[/]"
                    )
                    setattr(instance, "_session_cleaned_up", True)
                    return

                setattr(instance, "_cleanup_in_progress", True)
                console.print("[yellow]⚙️ Cleaning up session...[/]")

                try:
                    await instance.delete()
                except Exception as e:
                    console.print(
                        f"[yellow]⚠️ Non-critical error during cleanup: {str(e)}[/]"
                    )
                finally:
                    setattr(instance, "_cleanup_in_progress", False)

                setattr(instance, "_session_cleaned_up", True)
                console.print("[green]✓[/] Session cleaned up")
            except Exception as cleanup_error:
                console.print(
                    f"[red]✗[/] Failed to cleanup session: {str(cleanup_error)}"
                )

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await func(*args, **kwargs)

        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Process interrupted by user[/]")
            if args:
                await cleanup_session(args[0])
            raise SystemExit(130)

        except tuple(ERROR_MESSAGES.keys()) as e:
            error_config = ERROR_MESSAGES[type(e)]
            console.print(
                Panel(
                    f"[bold red]{error_config['title']}[/]\n\n"
                    f"[yellow]Details:[/] {str(e)}\n\n"
                    f"[blue]Suggestions:[/]\n"
                    + "".join(f"• {s}\n" for s in error_config["suggestions"]),
                    title="[red]Error",
                    border_style="red",
                )
            )
            if args:
                await cleanup_session(args[0])
            raise SystemExit(1)

        except Exception as e:
            console.print(
                Panel(
                    f"[bold red]Unexpected Error[/]\n\n"
                    f"[yellow]Error Type:[/] {type(e).__name__}\n"
                    f"[yellow]Details:[/] {str(e)}",
                    title="[red]System Error",
                    border_style="red",
                )
            )
            if args:
                await cleanup_session(args[0])
            raise SystemExit(1)

    return cast(Callable[..., Awaitable[T]], wrapper)
