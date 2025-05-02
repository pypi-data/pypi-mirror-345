import asyncio
import json
import logging
import os
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union

import requests
from dotenv import load_dotenv
from rich.console import Console

from shadai.core.decorators import handle_errors
from shadai.core.exceptions import (
    BadRequestError,
    ConfigurationError,
    IntelligenceAPIError,
    NetworkError,
    NotFoundError,
    ServerPermissionError,
    UnauthorizedError,
)
from shadai.core.schemas import JobResponse, JobStatus, JobType, SessionResponse

logger = logging.getLogger(__name__)
load_dotenv()

console = Console()


class IntelligenceAdapter:
    """Intelligence API adapter with robust error handling."""

    def __init__(self) -> None:
        """
        Initialize the adapter with configuration.

        Args:
            base_url (Optional[str]): Base URL for the API. Defaults to localhost.

        Raises:
            ConfigurationError: If SHADAI_API_KEY is not set.
        """
        self.core_base_url = "https://core.shadai.ai"
        self.core_api_base_url = "https://coreapi.shadai.ai"
        self.api_key = os.getenv("SHADAI_API_KEY")
        if not self.api_key:
            raise ConfigurationError("SHADAI_API_KEY environment variable not set")
        self._session = requests.Session()
        self._session.headers.update({"ApiKey": self.api_key})

    def _construct_url(self, endpoint: str, use_core_api_base_url: bool = False) -> str:
        """Construct the full URL from the base URL and endpoint."""
        if use_core_api_base_url:
            base_url = self.core_api_base_url
        else:
            base_url = self.core_base_url
        if not base_url.endswith("/"):
            base_url += "/"
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return base_url + endpoint

    @handle_errors
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        return_status_code: bool = False,
        use_core_api_base_url: bool = False,
        max_retries: int = 5,
        attempt: int = 0,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
        """Make HTTP request with retry logic and error handling.

        Args:
            method (str): The HTTP method to use
            endpoint (str): The endpoint to request
            return_status_code (bool): Whether to return the status code
            use_core_api_base_url (bool): Whether to use the core API base URL
            max_retries (int): The maximum number of retries
            attempt (int): The current attempt number
            **kwargs: Additional keyword arguments to pass to the request

        Returns:
            Union[Dict[str, Any], Tuple[Dict[str, Any], int]]: The response data

        Raises:
            RequestException: If no response is received from the server
            BadRequestError: If the request is invalid
            UnauthorizedError: If the request is unauthorized
            IntelligenceAPIError: If the request is invalid
            ServerPermissionError: If the request is forbidden
            NotFoundError: If the request is not found
        """
        error_map = {
            400: BadRequestError("Bad request"),
            401: UnauthorizedError("Unauthorized"),
            402: IntelligenceAPIError(
                "Insufficient balance. Please top up your account."
            ),
            403: ServerPermissionError("Server permission error"),
            404: NotFoundError("Not found"),
            500: IntelligenceAPIError("Internal server error"),
        }

        if attempt >= max_retries:
            raise IntelligenceAPIError("Max retries exceeded, request failed")

        try:
            url = self._construct_url(
                endpoint=endpoint, use_core_api_base_url=use_core_api_base_url
            )
            kwargs["timeout"] = kwargs.get("timeout", 25)

            response = self._session.request(method=method, url=url, **kwargs)

            if response is None:
                raise requests.RequestException("No response from the server")

            response.raise_for_status()
            json_response: Dict[str, Any] = response.json()
            data = json_response.get("data")

            return (data, response.status_code) if return_status_code else data

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            raise error_map.get(
                status_code, IntelligenceAPIError(f"HTTP error {status_code}: {e}")
            )

        except requests.exceptions.Timeout:
            return await self._make_request(
                method=method,
                endpoint=endpoint,
                return_status_code=return_status_code,
                use_core_api_base_url=use_core_api_base_url,
                max_retries=max_retries,
                attempt=attempt + 1,
                **kwargs,
            )

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException,
        ) as e:
            raise NetworkError(f"Request failed: {e}")

        except Exception as e:
            raise IntelligenceAPIError(f"Unexpected error: {e}")

    async def track_job(
        self,
        job_id: str,
        interval: float = 30.0,
        timeout: float = 300.0,
    ) -> JobResponse:
        """Track a job until completion without progress updates.

        Args:
            job_id: The job identifier
            interval: Time between checks in seconds
            timeout: Maximum wait time in seconds

        Returns:
            JobResponse: The completed job response

        Raises:
            IntelligenceAPIError: On timeout or failure
        """
        max_iterations = int(timeout // interval)

        for iteration in range(max_iterations):
            response = await self._make_request(
                method="GET",
                endpoint=f"/jobs/{job_id}",
                use_core_api_base_url=True,
            )

            job = JobResponse.model_validate(response)

            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                return job

            await asyncio.sleep(interval)

        raise IntelligenceAPIError(f"Job {job_id} timed out after {timeout}s")

    async def track_job_with_progress(
        self,
        job_id: str,
        interval: float = 30.0,
        timeout: float = 300.0,
    ) -> AsyncGenerator[Union[float, JobResponse], None]:
        """Track a job until completion with progress updates.

        Args:
            job_id: The job identifier
            interval: Time between checks in seconds
            timeout: Maximum wait time in seconds

        Yields:
            float: Progress updates (0.0 to 1.0)
            JobResponse: The final job response on completion

        Raises:
            IntelligenceAPIError: On timeout or failure
        """
        max_iterations = int(timeout // interval)

        for iteration in range(max_iterations):
            response = await self._make_request(
                method="GET",
                endpoint=f"/jobs/{job_id}",
                use_core_api_base_url=True,
            )

            job = JobResponse.model_validate(response)

            if hasattr(job, "progress") and job.progress is not None:
                yield job.progress
            else:
                yield 0.0

            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                return

            await asyncio.sleep(interval)

        raise IntelligenceAPIError(f"Job {job_id} timed out after {timeout}s")

    async def get_session(
        self, session_id: Optional[str] = None, alias: Optional[str] = None
    ) -> Optional[SessionResponse]:
        """Get session by ID or alias.

        Args:
            session_id (Optional[str]): The session identifier
            alias (Optional[str]): The alias to use for the session

        Returns:
            Optional[Dict[str, Any]]: The session response or None if not found

        Raises:
            IntelligenceAPIError: If session retrieval fails
        """
        try:
            if session_id is not None:
                response = await self._make_request(
                    method="GET",
                    endpoint="/sessions/detail",
                    use_core_api_base_url=True,
                    params={"session_id": session_id},
                )
            elif alias is not None:
                response = await self._make_request(
                    method="GET",
                    endpoint="/sessions/alias",
                    use_core_api_base_url=True,
                    params={"alias": alias},
                )
            else:
                raise IntelligenceAPIError(
                    "Either session_id or alias must be provided"
                )
            if response:
                return SessionResponse.model_validate(response)
            return None

        except Exception as e:
            logger.error("Failed to get session: %s", str(e))
            raise IntelligenceAPIError(f"Session retrieval failed: {str(e)}") from e

    async def create_session(self, type: str, **kwargs: Any) -> SessionResponse:
        """Create new processing session.

        Args:
            type: The type of session to create ("light", "standard", "deep")
            **kwargs: Additional session parameters

        Returns:
            SessionResponse: The created session

        Raises:
            IntelligenceAPIError: If session creation fails
        """
        try:
            session_data = {"config_name": type, **kwargs}
            response = await self._make_request(
                method="POST",
                endpoint="/sessions",
                json=session_data,
                use_core_api_base_url=True,
            )
            return SessionResponse.model_validate(response)

        except Exception as e:
            logger.error("Failed to create session: %s", str(e))
            raise IntelligenceAPIError(f"Session creation failed: {str(e)}") from e

    async def list_sessions(self) -> List[SessionResponse]:
        """List all sessions related to an user.

        Returns:
            List[SessionResponse]: A list of session responses

        Raises:
            IntelligenceAPIError: If session listing fails
        """
        try:
            response = await self._make_request(
                method="GET", endpoint="/sessions", use_core_api_base_url=True
            )
            return [
                SessionResponse.model_validate(item)
                for item in response.get("items", [])
            ]

        except Exception as e:
            logger.error("Failed to list sessions: %s", str(e))
            raise IntelligenceAPIError(f"Failed to list sessions: {str(e)}") from e

    async def delete_session(
        self, session_id: Optional[str] = None, alias: Optional[str] = None
    ) -> JobResponse:
        """Delete session by ID or alias.

        Args:
            session_id (Optional[str]): The session identifier to delete
            alias (Optional[str]): The alias to use for the session

        Returns:
            JobResponse: The job response

        Raises:
            IntelligenceAPIError: If deletion fails
        """
        if hasattr(self, "_cleanup_in_progress") and self._cleanup_in_progress:
            return None

        if session_id is None and alias is None:
            console.print("[yellow]⚠️ Cannot delete: Session ID or alias is required[/]")
            return None

        setattr(self, "_cleanup_in_progress", True)

        try:
            job = await self.create_job(
                input=session_id, job_type=JobType.DELETE_SESSION, session_id=session_id
            )

            if session_id is not None:
                await self._make_request(
                    method="DELETE",
                    endpoint="/sessions",
                    params={"session_id": session_id, "job_id": job.job_id},
                )
            elif alias is not None:
                await self._make_request(
                    method="DELETE",
                    endpoint="/sessions",
                    params={"alias": alias, "job_id": job.job_id},
                )
            return job

        except Exception as e:
            if hasattr(e, "response") and e.response.status_code == 404:
                console.print(
                    "[green]✓ Session is already deleted or does not exist[/]"
                )
            else:
                logger.error(f"Error deleting session: {str(e)}")
        finally:
            setattr(self, "_cleanup_in_progress", False)

    async def cleanup_namespace(self) -> JobResponse:
        """Cleanup the namespace.

        Returns:
            JobResponse: The job response

        Raises:
            IntelligenceAPIError: If cleanup fails
        """
        if (
            hasattr(self, "_namespace_cleanup_in_progress")
            and self._namespace_cleanup_in_progress
        ):
            console.print(
                "[yellow]⚠️ Namespace cleanup already in progress, skipping nested cleanup request[/]"
            )
            return

        setattr(self, "_namespace_cleanup_in_progress", True)

        try:
            _uuid = str(uuid.uuid4())
            job = await self.create_job(
                input="Cleanup namespace",
                job_type=JobType.CLEANUP_NAMESPACE,
                session_id=_uuid,
            )
            await self._make_request(
                method="DELETE",
                endpoint="/sessions",
                params={"job_id": job.job_id},
            )

            return job

        except Exception as e:
            logger.error(f"Error cleaning namespace: {str(e)}")
            raise IntelligenceAPIError(f"Error cleaning namespace: {str(e)}") from e

        finally:
            setattr(self, "_namespace_cleanup_in_progress", False)

    async def get_presigned_url(
        self,
        session_id: str,
        filename: str,
        destination: str,
    ) -> str:
        """Generate a pre-signed URL for file upload.

        Args:
            session_id (str): The session identifier
            filename (str): The filename to upload
            destination (str): The destination to upload the file to

        Returns:
            str: The pre-signed URL

        Raises:
            IntelligenceAPIError: If URL generation fails
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint="/ingestion",
                params={
                    "session_id": session_id,
                    "file_name": filename,
                    "destination": destination,
                },
                use_core_api_base_url=True,
            )
            return response

        except Exception as e:
            logger.error("Failed to generate upload URL: %s", str(e))
            raise IntelligenceAPIError(
                f"Failed to generate upload URL: {str(e)}"
            ) from e

    async def create_job(
        self, input: str, job_type: str, session_id: str
    ) -> JobResponse:
        """Create a job.

        Args:
            job_type (str): The type of job to create
            **kwargs: Additional keyword arguments to pass to the job

        Returns:
            str: The job ID
        """
        response = await self._make_request(
            method="POST",
            endpoint="/jobs",
            json={"input": input, "job_type": job_type, "session_id": session_id},
            use_core_api_base_url=True,
        )
        job = JobResponse.model_validate(response)
        return job

    async def ingest(self, session_id: str) -> JobResponse:
        """Start ingestion and track progress.

        Args:
            session_id: The session identifier

        Returns:
            JobResponse: The job response

        Raises:
            IntelligenceAPIError: If ingestion fails
        """
        try:
            job = await self.create_job(
                input=session_id, job_type=JobType.INGESTION, session_id=session_id
            )

            await self._make_request(
                method="POST",
                endpoint="/ingestion",
                params={"job_id": job.job_id, "session_id": session_id},
            )

            return job

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise IntelligenceAPIError(f"Ingestion failed: {e}") from e

    async def query(
        self,
        session_id: str,
        query: str,
        role: Optional[str] = None,
    ) -> JobResponse:
        """Execute query and wait for response.

        Args:
            session_id (str): The session identifier
            query (str): The query to execute
            role (Optional[str]): The role to use for the query

        Returns:
            JobResponse: The job response

        Raises:
            IntelligenceAPIError: If query fails or returns empty response after all retries
        """
        try:
            input = {
                "session_id": session_id,
                "query": query,
                "role": role,
            }
            job = await self.create_job(
                input=json.dumps(input),
                job_type=JobType.QUERY,
                session_id=session_id,
            )
            await self._make_request(
                method="GET",
                endpoint="/retrieval/query",
                params={
                    "job_id": job.job_id,
                    "session_id": session_id,
                    "query": query,
                    "role": role,
                },
            )
            return job
        except Exception as e:
            logger.error("Query failed: %s", str(e))
            raise IntelligenceAPIError(f"Query failed: {str(e)}") from e

    async def get_knowledge_summary(self, session_id: str) -> str:
        """Get session knowledge summary.

        Args:
            session_id (str): The session identifier

        Returns:
            JobResponse: The job response
        """
        try:
            job = await self.create_job(
                input=session_id, job_type=JobType.SUMMARY, session_id=session_id
            )
            await self._make_request(
                method="GET",
                endpoint="/retrieval/summary",
                params={"job_id": job.job_id, "session_id": session_id},
            )
            return job
        except Exception as e:
            logger.error("Failed to get knowledge summary: %s", str(e))
            raise IntelligenceAPIError(
                f"Failed to get knowledge summary: {str(e)}"
            ) from e

    async def create_article(self, session_id: str, topic: str) -> JobResponse:
        """Create an article on the topic.

        Args:
            session_id (str): The session identifier
            topic (str): The topic to create the article on

        Returns:
            JobResponse: The job response
        """
        try:
            job = await self.create_job(
                input=json.dumps({"session_id": session_id, "topic": topic}),
                job_type=JobType.ARTICLE,
                session_id=session_id,
            )
            await self._make_request(
                method="POST",
                endpoint="/retrieval/article",
                params={"job_id": job.job_id, "session_id": session_id},
                json={"topic": topic},
            )
            return job
        except Exception as e:
            logger.error("Failed to create article: %s", str(e))
            raise IntelligenceAPIError(f"Failed to create article: {str(e)}") from e

    async def chat(
        self,
        session_id: str,
        message: str,
        system_prompt: Optional[str] = None,
        use_images: bool = False,
        use_videos: bool = False,
    ) -> JobResponse:
        """Chat with the LLM using the session context and knowledge base.

        Args:
            session_id (str): The session identifier
            message (str): The message to send to the LLM
            system_prompt (Optional[str]): The system prompt to use for the chat
            use_images (bool): Whether to use images
            use_videos (bool): Whether to use videos

        Returns:
            JobResponse: The job response
        """
        try:
            job = await self.create_job(
                input=json.dumps(
                    {
                        "session_id": session_id,
                        "message": message,
                        "system_prompt": system_prompt,
                        "use_images": use_images,
                        "use_videos": use_videos,
                    }
                ),
                job_type=JobType.CHAT,
                session_id=session_id,
            )
            await self._make_request(
                method="POST",
                endpoint="/inference/chat",
                params={"job_id": job.job_id, "session_id": session_id},
                json={
                    "message": message,
                    "system_prompt": system_prompt,
                    "use_images": use_images,
                    "use_videos": use_videos,
                },
            )
            return job
        except Exception as e:
            logger.error("Failed to chat: %s", str(e))
            raise IntelligenceAPIError(f"Failed to chat: {str(e)}") from e

    async def llm_call(
        self,
        session_id: str,
        prompt: str,
        use_images: bool = False,
    ) -> JobResponse:
        """Call the LLM with the prompt.

        Args:
            session_id (str): The session identifier
            prompt (str): The prompt to send to the LLM
            use_images (bool): Whether to use images

        Returns:
            JobResponse: The job response
        """
        try:
            job = await self.create_job(
                input=json.dumps(
                    {
                        "session_id": session_id,
                        "prompt": prompt,
                        "use_images": use_images,
                    }
                ),
                job_type=JobType.COMPLETION,
                session_id=session_id,
            )
            await self._make_request(
                method="POST",
                endpoint="/inference/completion",
                params={"job_id": job.job_id, "session_id": session_id},
                json={
                    "prompt": prompt,
                    "use_images": use_images,
                },
            )
            return job
        except Exception as e:
            logger.error("Failed to call LLM: %s", str(e))
            raise IntelligenceAPIError(f"Failed to call LLM: {str(e)}") from e

    async def cleanup_chat(self, session_id: str) -> JobResponse:
        """
        Cleanup the chat history.

        Args:
            session_id (str): The session identifier to cleanup

        Returns:
            JobResponse: The job response

        Raises:
            IntelligenceAPIError: If cleanup fails
        """
        if not session_id:
            console.print("[yellow]⚠️ Cannot cleanup chat: Session ID is required[/]")
            return

        if (
            hasattr(self, "_chat_cleanup_in_progress")
            and self._chat_cleanup_in_progress
        ):
            console.print(
                "[yellow]⚠️ Chat cleanup already in progress, skipping nested cleanup request[/]"
            )
            return

        setattr(self, "_chat_cleanup_in_progress", True)

        try:
            job = await self.create_job(
                input=session_id, job_type=JobType.CLEANUP_CHAT, session_id=session_id
            )
            await self._make_request(
                method="DELETE",
                endpoint="/inference/cleanup-chat",
                params={"job_id": job.job_id, "session_id": session_id},
            )

            return job

        except IntelligenceAPIError:
            console.print(
                "[yellow]⚠️ Chat cleanup operation completed with errors. The chat history may be in an inconsistent state.[/]"
            )
        except Exception as e:
            logger.error(f"Error deleting chat: {str(e)}")
        finally:
            setattr(self, "_chat_cleanup_in_progress", False)
