import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def main():
    async with Session(type="standard", delete=True) as session:
        await session.ingest(input_dir=input_dir)
        await session.llm_call(
            prompt="¿Cual es el estado con la mayor economía en los Estados Unidos?",
            display_prompt=True,
            display_in_console=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
