from typing import List, Optional

from rich.console import Console
from rich.table import Table

from shadai.core.adapter import IntelligenceAdapter
from shadai.core.decorators import handle_errors
from shadai.core.schemas import SessionResponse

console = Console()


class Manager:
    def __init__(self) -> None:
        self._adapter = IntelligenceAdapter()

    async def __aenter__(self) -> "Manager":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @handle_errors
    async def list_sessions(
        self, show_in_console: bool = True
    ) -> List[SessionResponse]:
        """
        List all sessions related to an user

        Returns:
            List[SessionResponse]: A list of session responses
        """
        if show_in_console:
            with console.status("[bold yellow]Listing sessions...\n", spinner="dots"):
                sessions = await self._adapter.list_sessions()
                console.print(
                    f"\n[bold yellow]{len(sessions)} Session found for your user:[/]"
                )
                table = Table(
                    title="Sessions", show_header=True, header_style="bold white"
                )
                table.add_column("ID", style="blue")
                table.add_column("Alias", style="yellow")
                table.add_column("Config name", style="magenta")
                table.add_column("Language", style="blue")
                table.add_column("Cost", style="yellow")
                for session in sessions:
                    table.add_row(
                        session.session_id,
                        session.alias,
                        session.config_name,
                        session.language,
                        str(session.cost),
                    )
                console.print(table)
        else:
            return await self._adapter.list_sessions()

    @handle_errors
    async def delete_session(
        self, session_id: Optional[str] = None, alias: Optional[str] = None
    ) -> None:
        """
        Delete a session by its ID
        """
        if session_id is None and alias is None:
            raise ValueError("Session ID or alias is required")

        with console.status("[bold blue]🚀 Cleaning up session...[/]"):
            await self._adapter.delete_session(session_id=session_id, alias=alias)
            console.print("[bold green]✓[/] Session deleted successfully")

    @handle_errors
    async def cleanup_namespace(self) -> None:
        """
        Cleanup the namespace
        """
        with console.status("[bold blue]🚀 Cleaning up namespace...[/]"):
            await self._adapter.cleanup_namespace()
            console.print("[bold green]✓[/] Namespace cleaned up successfully")
