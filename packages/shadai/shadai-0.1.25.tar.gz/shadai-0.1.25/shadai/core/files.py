import logging
import os
from pathlib import Path
from typing import Literal

from requests.exceptions import RequestException
from rich.console import Console
from rich.progress import Progress

from shadai.core.adapter import IntelligenceAdapter

logger = logging.getLogger(__name__)
console = Console()


class FileManager:
    def __init__(self) -> None:
        self._adapter = IntelligenceAdapter()

    async def _count_files(self, input_path: Path) -> int:
        """Count the total number of files to process.

        Args:
            input_path (Path): The path to the directory containing the files to process.

        Returns:
            int: The total number of files to process.
        """
        return sum(1 for _ in input_path.rglob("*") if _.is_file())

    async def _upload_file(
        self,
        session_id: str,
        file_path: Path,
        destination: Literal["documents", "images", "videos"],
        progress: Progress,
        overall_task_id: int,
    ) -> None:
        """Upload a file to the session.

        Args:
            session_id (str): The session ID.
            file_path (Path): The path to the file to upload.
            destination (Literal["documents", "images", "videos"]): The destination to upload the file to.
            progress (Progress): The progress bar to update.
            overall_task_id (int): The ID of the overall task to update.
        """
        try:
            url = await self._adapter.get_presigned_url(
                session_id=session_id, filename=file_path.name, destination=destination
            )
            file_size = os.path.getsize(file_path)
            file_task_id = progress.add_task(
                f"[cyan]└─ {file_path.name}", total=file_size, start=True, visible=True
            )
            with open(file_path, "rb") as f:
                file_data = f.read()
            response = self._adapter._session.put(
                url,
                data=file_data,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(file_size),
                },
            )
            if not response.ok:
                raise RequestException(
                    f"Upload failed for {file_path.name}: {response.status_code}"
                )
            progress.update(
                task_id=file_task_id,
                completed=file_size,
                description=f"[green]└─ ✓ {file_path.name}",
                refresh=True,
            )
            progress.update(task_id=overall_task_id, advance=file_size, refresh=True)

        except Exception as e:
            if "file_task_id" in locals():
                progress.update(
                    task_id=file_task_id,
                    description=f"[red]└─ ✗ {file_path.name}",
                    refresh=True,
                )
            logger.error(f"Failed to upload {file_path.name}: {str(e)}")
            raise
