import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def ingest_with_alias(alias: str) -> None:
    """
    This function ingests a directory of documents into a session with a given alias.
    """
    async with Session(alias=alias, type="standard", delete=True) as session:
        await session.ingest(input_dir=input_dir)


async def ingest_without_alias() -> None:
    """
    This function ingests a directory of documents into a session without a given alias.
    """
    async with Session(type="standard", delete=True) as session:
        await session.ingest(input_dir=input_dir)


async def main():
    await ingest_with_alias(alias="my_alias")
    await ingest_without_alias()


if __name__ == "__main__":
    asyncio.run(main())
