import asyncio
import logging
import os
import random
from typing import Any, AsyncGenerator, Dict, List, Literal, Optional, Tuple, Union

from dotenv import load_dotenv
from requests import RequestException, Session
from rich.console import Console

from shadai.core.exceptions import ConfigurationError, IntelligenceAPIError
from shadai.core.schemas import JobResponse, JobStatus, SessionCreate, SessionResponse

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
        self._session = Session()
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

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        return_status_code: bool = False,
        use_core_api_base_url: bool = False,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
        """Make HTTP request with retry logic and error handling."""
        url = self._construct_url(
            endpoint=endpoint, use_core_api_base_url=use_core_api_base_url
        )
        kwargs["timeout"] = kwargs.get("timeout", 25)

        response = self._session.request(method=method, url=url, **kwargs)

        if response is None:
            raise RequestException("No response from the server")

        if response.status_code == 402:
            raise IntelligenceAPIError(
                "Insufficient balance. Please top up your account."
            )
        response.raise_for_status()
        json_response = response.json()
        if return_status_code:
            return json_response.get("data"), response.status_code
        return json_response.get("data")

    async def warm_up(self, total_timeout: float = 120.0) -> bool:
        """
        Ensures the Lambda service is ready by hitting the health endpoint.
        Keeps trying until the endpoint returns 200 OK or times out.

        Args:
            total_timeout: Maximum time to spend on warm-up in seconds. Defaults to 120.0 (2 minutes).

        Returns:
            bool: True if service is ready, False otherwise
        """
        logger.debug("Checking service health...")

        start_time = asyncio.get_event_loop().time()

        try:
            _, status_code = await self._make_request(
                method="GET", endpoint="/health", return_status_code=True, timeout=3
            )
            if status_code == 200:
                logger.debug("Service is warm, health check successful")
                return True
        except Exception:
            pass

        while (asyncio.get_event_loop().time() - start_time) < total_timeout:
            try:
                _, status_code = await self._make_request(
                    method="GET", endpoint="/health", return_status_code=True, timeout=5
                )
                if status_code == 200:
                    logger.debug("Service is now warm, health check successful")
                    return True
            except Exception:
                await asyncio.sleep(5)

        logger.warning(f"Service warm-up timed out after {total_timeout} seconds")
        return False

    async def _get_job_status(
        self, job_id: str, max_retries: int = 5, retry_delay: float = 1.0
    ) -> JobResponse:
        """
        Get the status of a job with retry for None responses.

        Args:
            job_id: The job identifier
            max_retries: Maximum number of retries for None responses
            retry_delay: Initial delay between retries (with exponential backoff)

        Returns:
            JobResponse: The job status response

        Raises:
            IntelligenceAPIError: If job status check fails after all retries
        """
        for attempt in range(max_retries):
            try:
                response = await self._make_request(
                    method="GET", endpoint=f"/jobs/{job_id}", use_core_api_base_url=True
                )
                if response is None:
                    if attempt < max_retries - 1:
                        backoff_delay = (
                            retry_delay * (2**attempt) * (1 + random.random() * 0.1)
                        )
                        logger.warning(
                            f"Job status check received None response (attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {backoff_delay:.2f} seconds..."
                        )
                        await asyncio.sleep(backoff_delay)
                        continue
                    else:
                        raise IntelligenceAPIError(
                            f"Job status check failed: Received None response after {max_retries} attempts"
                        )

                return JobResponse.model_validate(response)

            except Exception as e:
                if attempt < max_retries - 1 and "NoneType" in str(e):
                    backoff_delay = (
                        retry_delay * (2**attempt) * (1 + random.random() * 0.1)
                    )
                    await asyncio.sleep(backoff_delay)
                    continue
                else:
                    logger.error("Failed to get job status: %s", str(e))
                    raise IntelligenceAPIError(
                        f"Failed to get job status: {str(e)}"
                    ) from e

    async def _poll_job(
        self, job_id: str, interval: float
    ) -> AsyncGenerator[JobResponse, None]:
        """
        Poll job status until completion.

        Args:
            job_id (str): The job identifier to poll
            interval (float): Time in seconds between polls

        Yields:
            JobResponse: Current status of the job
        """
        retries = 0
        max_consecutive_failures = 5

        while True:
            try:
                response = await self._get_job_status(job_id=job_id)
                retries = 0
                yield response

                if response.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    break

                await asyncio.sleep(interval)

            except Exception as e:
                retries += 1
                if retries < max_consecutive_failures:
                    logger.warning(
                        f"Job polling failed (attempt {retries}/{max_consecutive_failures}), "
                        f"retrying in {interval} seconds... Error: {str(e)}"
                    )
                    await asyncio.sleep(interval)
                    continue
                else:
                    logger.error(
                        f"Job polling failed after {max_consecutive_failures} attempts: {str(e)}"
                    )
                    raise

    async def _wait_until_final_status(
        self, poll_generator: AsyncGenerator[JobResponse, None], timeout: float
    ) -> JobResponse:
        """
        Wait until job reaches a final status (COMPLETED or FAILED).

        Args:
            poll_generator: The polling generator
            timeout: Maximum time to wait in seconds

        Returns:
            JobResponse with final status

        Raises:
            TimeoutError if timeout is reached
        """

        while True:
            response = await asyncio.wait_for(
                poll_generator.__anext__(), timeout=timeout
            )
            if response.status in {JobStatus.COMPLETED, JobStatus.FAILED}:
                return response

    async def _wait_until_final_status_with_progress(
        self, poll_generator: AsyncGenerator[JobResponse, None], timeout: float
    ) -> AsyncGenerator[Union[float, JobResponse], None]:
        """
        Wait until job reaches a final status (COMPLETED or FAILED), yielding progress updates.
        This is specifically designed for operations that need progress tracking like ingestion.

        Args:
            poll_generator: The polling generator
            timeout: Maximum time to wait in seconds

        Yields:
            - Float values representing progress (0.0 to 1.0) during processing
            - Final JobResponse with COMPLETED or FAILED status

        Raises:
            TimeoutError if timeout is reached
        """
        while True:
            response = await asyncio.wait_for(
                poll_generator.__anext__(), timeout=timeout
            )
            if hasattr(response, "progress") and response.progress is not None:
                yield response.progress  # Yield the progress float

            if response.status in {JobStatus.COMPLETED, JobStatus.FAILED}:
                yield response
                break

    async def _wait_for_job(
        self,
        job_id: str,
        polling_interval: float = 10.0,
        timeout: float = 30,
        max_retries: int = 5,
    ) -> str:
        """
        Wait for job completion with timeout and retry on temporary service unavailability.

        Args:
            job_id (str): The job identifier to wait for
            polling_interval (float): Time in seconds between status checks. Defaults to 10.0.
            timeout (float): Maximum time to wait in seconds. Defaults to 30.
            max_retries (int): Maximum number of consecutive retries on failure. Defaults to 5.

        Returns:
            str: The job result data

        Raises:
            IntelligenceAPIError: If job fails, times out, or exceeds max attempts
        """
        is_deletion_job = "delete" in job_id.lower() or "cleanup" in job_id.lower()

        try:
            poll_generator = self._poll_job(job_id=job_id, interval=polling_interval)

            response = await self._wait_until_final_status(
                poll_generator=poll_generator, timeout=timeout * 1.5
            )

            if response.status == JobStatus.COMPLETED:
                if response.result is None:
                    if not is_deletion_job:
                        logger.warning(
                            f"Job {job_id} completed but returned None result, treating as empty response"
                        )
                    return "Empty response from the server. The data might still be processing."
                return response.result

            if response.status == JobStatus.FAILED:
                error_message = response.result if response.result else "Unknown error"

                if is_deletion_job:
                    return f"Job failed: {error_message}"
                raise IntelligenceAPIError(f"Job {job_id} failed: {error_message}")

            if not is_deletion_job:
                logger.error(
                    f"Job {job_id} ended with unexpected status: {response.status}"
                )
            raise IntelligenceAPIError(
                f"Job {job_id} ended with unexpected status: {response.status}"
            )

        except asyncio.TimeoutError:
            if not is_deletion_job:
                logger.error(f"Job {job_id} timed out after {timeout} seconds")

            if is_deletion_job:
                return f"Job failed: Timed out after {timeout} seconds"

            raise IntelligenceAPIError(
                f"Job {job_id} timed out after {timeout} seconds. The service may be experiencing high load."
            )
        except Exception as e:
            logger.error(f"Error waiting for job {job_id}: {str(e)}")
            raise IntelligenceAPIError(
                f"Error waiting for job {job_id}: {str(e)}"
            ) from e

    async def _wait_for_ingestion_job(
        self,
        job_id: str,
        polling_interval: float = 30.0,
        timeout: float = 3600,
    ) -> AsyncGenerator[float, None]:
        """
        Wait for ingestion job completion with extended timeout and robust error handling
        specifically designed for long-running ingestion tasks.

        Args:
            job_id (str): The job identifier to wait for
            polling_interval (float): Time in seconds between status checks. Defaults to 30.0.
            timeout (float): Maximum time to wait in seconds. Defaults to 3600 (1 hour).

        Yields:
            float: Progress values representing progress (0.0 to 1.0) during processing

        Raises:
            IntelligenceAPIError: If job fails, times out, or exceeds max attempts
        """
        try:
            yield 0.01
            current_progress = 0.01

            poll_generator = self._poll_job(job_id=job_id, interval=polling_interval)

            async for (
                progress_or_response
            ) in self._wait_until_final_status_with_progress(
                poll_generator=poll_generator, timeout=timeout
            ):
                if isinstance(progress_or_response, float):
                    if progress_or_response > current_progress:
                        current_progress = progress_or_response
                        yield min(0.99, current_progress)
                    continue

                if hasattr(progress_or_response, "status"):
                    if progress_or_response.status == JobStatus.FAILED:
                        error_message = (
                            progress_or_response.result
                            or "Job failed without specific error"
                        )
                        logger.error(f"Ingestion job {job_id} failed: {error_message}")
                        raise IntelligenceAPIError(
                            f"Ingestion job {job_id} failed: {error_message}"
                        )

                    if progress_or_response.status == JobStatus.COMPLETED:
                        await asyncio.sleep(1)
                        yield 1.0
                        return

        except asyncio.TimeoutError:
            logger.error(f"Ingestion job {job_id} timed out after {timeout} seconds")
            raise IntelligenceAPIError(
                f"Ingestion job {job_id} timed out after {timeout} seconds. "
            )
        except Exception as e:
            logger.error(f"Error waiting for ingestion job {job_id}: {str(e)}")
            raise IntelligenceAPIError(
                f"Error waiting for ingestion job {job_id}: {str(e)}"
            ) from e

    async def _handle_job_with_retries(
        self,
        job_response: dict,
        operation_name: str,
        max_retries: int = 3,
        retry_delay: int = 5,
        polling_interval: int = 5,
        timeout: int = 180,
    ) -> str:
        """
        Handle job execution with retries for empty responses.

        Args:
            job_response: The response containing the job ID
            operation_name: Name of the operation for logging
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            polling_interval: Interval for polling job status
            timeout: Timeout for job completion

        Returns:
            str: The job result

        Raises:
            IntelligenceAPIError: If job fails or returns empty response after all retries
        """
        for attempt in range(max_retries):
            response = await self._wait_for_job(
                job_id=job_response.get("job_id"),
                polling_interval=polling_interval,
                timeout=timeout,
            )
            if "empty response" not in response.lower():
                return response

            if attempt < max_retries - 1:
                logger.warning(
                    f"{operation_name} returned 'Empty response' on attempt {attempt + 1}/{max_retries}, retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
                continue

        raise IntelligenceAPIError(
            f"{operation_name} returned 'Empty response' after all retry attempts. The server might still be processing the data."
        )

    async def get_session(
        self, session_id: Optional[str] = None, alias: Optional[str] = None
    ) -> Optional[SessionResponse]:
        """Get session by ID.

        Args:
            session_id (Optional[str]): The session identifier
            alias (Optional[str]): The alias to use for the session
        Returns:
            Optional[SessionResponse]: The session response or None if the session is not found

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
            if alias is not None and (response is None or not response):
                return None
            return SessionResponse.model_validate(response)
        except Exception as e:
            logger.error("Failed to get session: %s", str(e))
            raise IntelligenceAPIError(f"Session retrieval failed: {str(e)}") from e

    async def list_sessions(self) -> List[SessionResponse]:
        """
        List all sessions related to an user

        Returns:
            List[SessionResponse]: A list of session responses
        """
        try:
            response = await self._make_request(
                method="GET", endpoint="/sessions", use_core_api_base_url=True
            )
            items = response.get("items", [])
            return [SessionResponse.model_validate(session) for session in items]
        except Exception as e:
            logger.error("Failed to list sessions: %s", str(e))
            raise IntelligenceAPIError(f"Failed to list sessions: {str(e)}") from e

    async def create_session(
        self, type: Literal["light", "standard", "deep"], **kwargs: Any
    ) -> SessionResponse:
        """
        Create new processing session.

        Args:
            type: The type of session to create
            **kwargs: Additional session parameters

        Returns:
            SessionResponse: The created session

        Raises:
            IntelligenceAPIError: If session creation fails after all retries
        """
        session_create = SessionCreate(config_name=type, **kwargs)
        response = await self._make_request(
            method="POST",
            endpoint="/sessions",
            json=session_create.model_dump(exclude_none=True),
            use_core_api_base_url=True,
        )
        session_response = SessionResponse.model_validate(response)
        return session_response

    async def delete_session(
        self, session_id: Optional[str] = None, alias: Optional[str] = None
    ) -> None:
        """
        Delete session and wait for completion.

        Args:
            session_id (Optional[str]): The session identifier to delete
            alias (Optional[str]): The alias to use for the session
        Raises:
            IntelligenceAPIError: If deletion fails
        """
        if hasattr(self, "_cleanup_in_progress") and self._cleanup_in_progress:
            return

        if session_id is None and alias is None:
            console.print("[yellow]⚠️ Cannot delete: Session ID or alias is required[/]")
            return

        # Set flag to prevent recursive cleanup
        setattr(self, "_cleanup_in_progress", True)

        try:
            if session_id is not None:
                response = await self._make_request(
                    method="DELETE",
                    endpoint="/sessions",
                    params={"session_id": session_id},
                )
            elif alias is not None:
                response = await self._make_request(
                    method="DELETE",
                    endpoint="/sessions",
                    params={"alias": alias},
                )
            # Handle case where response is None or missing job_id
            if not response or "job_id" not in response:
                console.print(
                    "[yellow]⚠️ Session deletion returned no job ID, session may already be deleted[/]"
                )
                return

            try:
                # Don't raise exceptions for delete job failures
                await self._wait_for_job(
                    job_id=response.get("job_id"), polling_interval=5, timeout=180
                )
                console.print("[green]✓ Session deleted successfully[/]")

            except IntelligenceAPIError:
                console.print(
                    "\n[yellow]⚠️ Delete operation completed with errors. The session may already be deleted or in an inconsistent state.[/]"
                )

        except Exception as e:
            if hasattr(e, "response") and e.response.status_code == 404:
                console.print(
                    "[green]✓ Session is already deleted or does not exist[/]"
                )
            else:
                logger.error(f"Error deleting session: {str(e)}")
        finally:
            # Always reset the cleanup flag, even if an exception occurs
            setattr(self, "_cleanup_in_progress", False)

    async def cleanup_namespace(self) -> None:
        """
        Cleanup the namespace

        Raises:
            IntelligenceAPIError: If cleanup fails
        """
        # Add a static flag to prevent recursive cleanup attempts
        if (
            hasattr(self, "_namespace_cleanup_in_progress")
            and self._namespace_cleanup_in_progress
        ):
            console.print(
                "[yellow]⚠️ Namespace cleanup already in progress, skipping nested cleanup request[/]"
            )
            return

        # Set flag to prevent recursive cleanup
        setattr(self, "_namespace_cleanup_in_progress", True)

        try:
            response = await self._make_request(
                method="DELETE",
                endpoint="/sessions",
            )

            # Handle case where response is None or missing job_id
            if not response or "job_id" not in response:
                console.print(
                    "[yellow]⚠️ Namespace cleanup returned no job ID, namespace may already be empty[/]"
                )
                return

            try:
                # Don't raise exceptions for cleanup job failures
                job_result = await self._wait_for_job(
                    job_id=response.get("job_id"), polling_interval=5, timeout=180
                )

                # If the job result starts with "Job failed", it means the job failed but we're suppressing the error
                if job_result.startswith("Job failed:"):
                    # Only show a concise error message without the full job ID and error details
                    console.print(
                        "[yellow]⚠️ Cleanup operation completed with errors[/]"
                    )
                    console.print(
                        "[yellow]The namespace may be in an inconsistent state[/]"
                    )
                else:
                    # Normal success case
                    console.print("[green]✓ Namespace cleaned up successfully[/]")

            except IntelligenceAPIError:
                console.print("[yellow]⚠️ Cleanup operation completed with errors[/]")
                console.print(
                    "[yellow]The namespace may be in an inconsistent state[/]"
                )

        except Exception as e:
            logger.error(f"Error deleting namespace: {str(e)}")
        finally:
            setattr(self, "_namespace_cleanup_in_progress", False)

    async def get_presigned_url(
        self,
        session_id: str,
        filename: str,
        destination: Literal["documents", "images", "videos"],
    ) -> str:
        """Generate a pre-signed URL for file upload.

        Args:
            session_id (str): The session identifier
            filename (str): The filename to upload
            destination (Literal["documents", "images", "videos"]): The destination to upload the file to
        Returns:
            str: The pre-signed URL
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

    async def ingest(self, session_id: str) -> AsyncGenerator[float, None]:
        """
        Start ingestion process and yield progress values as available.
        This method only yields progress updates (0.0-1.0), not the final result.

        Args:
            session_id (str): The session identifier for ingestion

        Yields:
            float: Progress values representing progress (0.0 to 1.0) during processing

        Raises:
            IntelligenceAPIError: If ingestion fails
        """
        try:
            response = await self._make_request(
                method="POST", endpoint="/ingestion", params={"session_id": session_id}
            )

            if not response or "job_id" not in response:
                logger.warning(
                    f"Ingestion request returned invalid response: {response}"
                )
                raise IntelligenceAPIError(
                    f"Ingestion failed: Invalid API response - {response}"
                )

            job_id = response.get("job_id")

            final_progress_yielded = False

            async for progress in self._wait_for_ingestion_job(
                job_id=job_id,
                polling_interval=30.0,
                timeout=3600,
            ):
                if progress >= 0.999:
                    final_progress_yielded = True

                yield progress

            if not final_progress_yielded:
                yield 1.0

            try:
                final_status = await self._get_job_status(job_id=job_id)
                if final_status.status != JobStatus.COMPLETED:
                    logger.warning(
                        f"Ingestion job {job_id} reported completion but status is {final_status.status}"
                    )
            except Exception as e:
                logger.warning(f"Error during final job status check: {str(e)}")

        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
            raise IntelligenceAPIError(f"Ingestion failed: {str(e)}") from e

    async def query(
        self,
        session_id: str,
        query: str,
        role: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
    ) -> str:
        """Execute query and wait for response.

        Args:
            session_id (str): The session identifier
            query (str): The query to execute
            role (Optional[str]): The role to use for the query
            max_retries (int): Maximum number of retry attempts
            retry_delay (int): Delay between retries in seconds

        Returns:
            str: The query response

        Raises:
            IntelligenceAPIError: If query fails or returns empty response after all retries
        """
        try:
            job_response = await self._make_request(
                method="GET",
                endpoint="/retrieval/query",
                params={"session_id": session_id, "query": query, "role": role},
            )
            return await self._handle_job_with_retries(
                job_response=job_response,
                operation_name="Query",
                max_retries=max_retries,
                retry_delay=retry_delay,
            )
        except Exception as e:
            logger.error("Query failed: %s", str(e))
            raise IntelligenceAPIError(f"Query failed: {str(e)}") from e

    async def get_knowledge_summary(self, session_id: str) -> str:
        """Get session knowledge summary.

        Args:
            session_id (str): The session identifier

        Returns:
            str: The knowledge summary
        """
        try:
            job_response = await self._make_request(
                method="GET",
                endpoint="/retrieval/summary",
                params={"session_id": session_id},
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="Knowledge summary"
            )
        except Exception as e:
            logger.error("Failed to get knowledge summary: %s", str(e))
            raise IntelligenceAPIError(
                f"Failed to get knowledge summary: {str(e)}"
            ) from e

    async def create_article(self, session_id: str, topic: str) -> str:
        """Create an article on the topic.

        Args:
            session_id (str): The session identifier
            topic (str): The topic to create the article on

        Returns:
            str: The article creation response
        """
        try:
            job_response = await self._make_request(
                method="POST",
                endpoint="/retrieval/article",
                params={"session_id": session_id},
                json={"topic": topic},
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="Article creation"
            )
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
    ) -> str:
        """Chat with the LLM using the session context and knowledge base.

        Args:
            session_id (str): The session identifier
            message (str): The message to send to the LLM
            system_prompt (Optional[str]): The system prompt to use for the chat
            use_images (bool): Whether to use images
            use_videos (bool): Whether to use videos

        Returns:
            str: The chat response
        """
        try:
            job_response = await self._make_request(
                method="POST",
                endpoint="/inference/chat",
                params={"session_id": session_id},
                json={
                    "message": message,
                    "system_prompt": system_prompt,
                    "use_images": use_images,
                    "use_videos": use_videos,
                },
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="Chat"
            )
        except Exception as e:
            logger.error("Failed to chat: %s", str(e))
            raise IntelligenceAPIError(f"Failed to chat: {str(e)}") from e

    async def llm_call(
        self,
        session_id: str,
        prompt: str,
        use_images: bool = False,
    ) -> str:
        """Call the LLM with the prompt.

        Args:
            session_id (str): The session identifier
            prompt (str): The prompt to send to the LLM
            use_images (bool): Whether to use images

        Returns:
            str: The LLM response
        """
        try:
            job_response = await self._make_request(
                method="POST",
                endpoint="/inference/completion",
                params={"session_id": session_id},
                json={
                    "prompt": prompt,
                    "use_images": use_images,
                },
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="LLM call"
            )
        except Exception as e:
            logger.error("Failed to call LLM: %s", str(e))
            raise IntelligenceAPIError(f"Failed to call LLM: {str(e)}") from e

    async def cleanup_chat(self, session_id: str) -> None:
        """
        Cleanup the chat history.

        Args:
            session_id (str): The session identifier to cleanup
        Raises:
            IntelligenceAPIError: If cleanup fails
        """
        if not session_id:
            console.print("[yellow]⚠️ Cannot cleanup chat: Session ID is required[/]")
            return

        # Add a static flag to prevent recursive cleanup attempts
        if (
            hasattr(self, "_chat_cleanup_in_progress")
            and self._chat_cleanup_in_progress
        ):
            console.print(
                "[yellow]⚠️ Chat cleanup already in progress, skipping nested cleanup request[/]"
            )
            return

        # Set flag to prevent recursive cleanup
        setattr(self, "_chat_cleanup_in_progress", True)

        try:
            job_response = await self._make_request(
                method="DELETE",
                endpoint="/inference/cleanup-chat",
                params={"session_id": session_id},
            )

            # Handle case where response is None or missing job_id
            if not job_response or "job_id" not in job_response:
                console.print(
                    "[yellow]⚠️ Chat cleanup returned no job ID, chat history may already be empty[/]"
                )
                return

            # Don't raise exceptions for cleanup job failures
            await self._wait_for_job(
                job_id=job_response.get("job_id"), polling_interval=5, timeout=180
            )
            console.print("[green]✓ Chat history cleaned up successfully[/]")

        except IntelligenceAPIError:
            console.print(
                "[yellow]⚠️ Chat cleanup operation completed with errors. The chat history may be in an inconsistent state.[/]"
            )
        except Exception as e:
            logger.error(f"Error deleting chat: {str(e)}")
        finally:
            setattr(self, "_chat_cleanup_in_progress", False)
