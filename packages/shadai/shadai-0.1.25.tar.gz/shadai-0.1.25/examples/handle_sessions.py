import asyncio
import os
import sys
from typing import List, Optional

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from shadai.core.enums import AIModels, QueryMode
from shadai.core.manager import Manager
from shadai.core.schemas import SessionResponse
from shadai.core.session import Session


async def create_session(alias: Optional[str] = None) -> Session:
    """
    This function creates a new session with specific parameters.
    You can customize model, temperature, tokens, and query mode.
    If you set delete to False, you need to manually delete the session.

    Returns:
        Session: The session object.
    """
    async with Session(
        alias=alias,
        type="standard",
        llm_model=AIModels.CLAUDE_3_7_SONNET,
        llm_temperature=0.7,
        llm_max_tokens=4096,
        query_mode=QueryMode.HYBRID,
        delete=True,
    ) as session:
        return session


async def get_existing_session_with_session_id(session_id: str) -> Session:
    """
    This function gets a session by its ID.

    Args:
        session_id (str): The ID of the session to get.

    Returns:
        Session: The session object.
    """
    async with Session(session_id=session_id, type="standard", delete=False) as session:
        return session


async def get_existing_session_with_alias(alias: str) -> Session:
    """
    This function gets a session by its alias.

    Args:
        session_id (str): The ID of the session to get.

    Returns:
        Session: The session object.
    """
    async with Session(alias=alias, type="standard", delete=False) as session:
        return session


async def list_sessions() -> List[SessionResponse]:
    """
    This function lists all the sessions in the current namespace.
    Returns:
        List[SessionResponse]: A list of session responses.
    """
    async with Manager() as manager:
        sessions = await manager.list_sessions(show_in_console=True)
        return sessions


async def cleanup_namespace() -> None:
    """
    This function cleans up the namespace of the current session.
    """
    async with Manager() as manager:
        await manager.cleanup_namespace()


async def delete_session(
    session_id: Optional[str] = None, alias: Optional[str] = None
) -> None:
    """
    This function deletes a session by its ID.

    Args:
        session_id (str): The ID of the session to delete.
    """
    async with Manager() as manager:
        await manager.delete_session(session_id=session_id, alias=alias)


async def main():
    await create_session(alias="test-session")
    await list_sessions()
    await delete_session(session_id="YOUR SESSION ID")
    await cleanup_namespace()


if __name__ == "__main__":
    asyncio.run(main())
