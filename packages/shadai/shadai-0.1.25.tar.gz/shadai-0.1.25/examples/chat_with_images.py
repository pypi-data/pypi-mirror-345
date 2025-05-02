import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.session import Session

images_dir = os.path.join(os.path.dirname(__file__), "media", "images")


async def chat_with_images_without_history():
    """
    This function chats with the images.
    """
    async with Session(
        type="standard",
        delete=True,
    ) as session:
        await session.llm_call(
            prompt="Dame toda la información que puedas obtener de estas imágenes",
            images_path=images_dir,
            display_prompt=True,
            display_in_console=True,
        )


if __name__ == "__main__":
    asyncio.run(chat_with_images_without_history())
