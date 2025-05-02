from typing import Any, Awaitable, Callable, Optional, Union

from shadai.core.decorators import handle_errors
from shadai.core.exceptions import (
    AgentConfigurationError,
    AgentExecutionError,
    AgentFunctionError,
)
from shadai.core.session import Session


class ToolAgent:
    def __init__(
        self,
        session: Session,
        prompt: str,
        use_summary: bool,
        function: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
        is_async_function: bool = False,
    ):
        """
        Initialize the ToolAgent with required parameters

        Args:
            session: The Session object containing document context and LLM configuration
            prompt: System prompt defining agent's role and how to use documents and function_data to answer
            use_summary: Boolean indicating whether to include ingested documents in context
            function: Callable that returns data for the agent to process (can be sync or async)
            is_async_function: Whether the provided function is async
        """
        self.session = session
        self.function = function
        self.prompt = prompt
        self.use_summary = use_summary
        self.is_async_function = is_async_function

    async def _get_context(self) -> Optional[str]:
        """
        Gather context from documents if use_summary is True
        """
        try:
            if self.use_summary:
                return await self.session.summarize()
            return None
        except Exception as e:
            raise AgentExecutionError(f"Failed to get context: {str(e)}") from e

    async def _get_function_data(self, **kwargs: Any) -> Any:
        """
        Execute the provided function and get its data

        Args:
            **kwargs: Additional keyword arguments to pass to the function

        Returns:
            Any: The result of the function call
        """
        try:
            if self.is_async_function:
                return await self.function(**kwargs)
            return self.function(**kwargs)
        except Exception as e:
            raise AgentFunctionError(f"Function execution failed: {str(e)}") from e

    @handle_errors
    async def call(
        self,
        display_prompt: bool = False,
        display_in_console: bool = True,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Execute asynchronously the agent's task and return the response

        Args:
            display_prompt (bool): Whether to display the prompt
            display_in_console (bool): Whether to display the response in the console
            **kwargs: Additional keyword arguments to pass to the function

        Returns:
            Optional[str]: Generated response from the agent, or None if an error occurred
        """
        if self.use_summary and "{summary}" not in self.prompt:
            raise AgentConfigurationError(
                "Prompt must contain '{summary}' when use_summary is True"
            )

        if not self.use_summary and "{function_output}" not in self.prompt:
            raise AgentConfigurationError(
                "Prompt must contain '{function_output}' when use_summary is False"
            )

        context = await self._get_context()

        if self.use_summary and context is None:
            raise AgentExecutionError("Failed to get summary from session")

        function_output = await self._get_function_data(**kwargs)

        if function_output is None:
            raise AgentFunctionError("Function returned None")

        format_args = {"function_output": function_output}

        if self.use_summary:
            format_args["summary"] = context

        formatted_prompt = self.prompt.format(**format_args)

        response = await self.session.llm_call(
            prompt=formatted_prompt,
            display_prompt=display_prompt,
            display_in_console=display_in_console,
        )

        if response is None:
            raise AgentExecutionError("LLM call returned None")

        return response
