# SHADAI Intelligence Client

A Python client for interacting with the SHADAI API. This client provides a simple interface for document processing, querying, and session management.

## Installation

```bash
pip install shadai
```

## Requirements

- Python >= 3.9
- Environment Variables:
  - `SHADAI_API_KEY`: Your SHADAI API key

## Features

- Asynchronous API interactions
- Automatic session management
- File ingestion with progress tracking
- Interactive query interface
- Robust error handling and retries
- Rich console output

## Getting Started with SHADAI

SHADAI Intelligence Client is a powerful tool for document processing, querying, and AI-assisted analysis. This guide will walk you through various use cases and show you how to leverage the full capabilities of the platform.

### Session Configuration

When working with SHADAI, you'll always start by creating a Session. Here are the configuration options available:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| type | str | Processing type ("light", "standard", "deep") | "standard" |
| llm_model | str | Language model to use | AIModels.CLAUDE_3_5_HAIKU |
| llm_temperature | float | Model temperature | 0.7 |
| llm_max_tokens | int | Maximum tokens for response | 4096 |
| query_mode | str | Query processing mode | hybrid |
| language | str | Response language | es |
| delete | bool | Auto-delete session on exit | True |

## Working with Documents

### Ingesting Documents

The first step in most SHADAI workflows is ingesting documents. SHADAI can process various document formats and extract relevant information.

```python
# examples/ingest_data.py
import asyncio
import os
from shadai.core.session import Session

# Define the directory containing your documents
input_dir = os.path.join(os.path.dirname(__file__), "data")

async def ingest_with_alias(alias: str) -> None:
    """
    Creating a session with an alias allows you to easily reference it later.
    This is useful for long-running projects where you might need to
    come back to the same document set.
    """
    async with Session(alias=alias, type="standard", delete=True) as session:
        # The ingest method processes all documents in the input directory
        # It automatically handles different file formats and extracts text content
        await session.ingest(input_dir=input_dir)
        print(f"Successfully ingested documents into session with alias: {alias}")

async def ingest_without_alias() -> None:
    """
    If you don't need to reference the session later, you can create one
    without an alias. This is useful for one-off queries.
    """
    async with Session(type="standard", delete=True) as session:
        await session.ingest(input_dir=input_dir)
        print(f"Successfully ingested documents into session with ID: {session.id}")

async def main():
    # Example using both approaches
    await ingest_with_alias(alias="constitution_docs")
    await ingest_without_alias()

if __name__ == "__main__":
    asyncio.run(main())
```

### Managing Sessions

SHADAI provides tools for managing your sessions, including creating, listing, retrieving, and deleting them.

```python
# examples/handle_sessions.py
import asyncio
from shadai.core.manager import Manager
from shadai.core.session import Session
from shadai.core.constants import AIModels, QueryMode

async def create_session() -> Session:
    """
    This function creates a new session with specific parameters.
    You can customize model, temperature, tokens, and query mode.
    If you set delete to False, you need to manually delete the session.

    Returns:
        Session: The session object.
    """
    async with Session(
        type="standard",
        llm_model=AIModels.CLAUDE_3_7_SONNET,   # Specify which LLM to use
        llm_temperature=0.7,                    # Control response creativity (0.0-1.0)
        llm_max_tokens=4096,                    # Set maximum response length
        query_mode=QueryMode.HYBRID,            # Choose between HYBRID, SEMANTIC_HYBRID, TEXT_SEARCH, etc
        delete=False,                           # No auto-delete session when done
    ) as session:
        # Session is now ready for document ingestion and queries
        return session

async def get_existing_session_with_session_id(session_id: str) -> Session:
    """
    Retrieve a previously created session using its ID.
    Setting delete=False ensures the session isn't deleted when the context manager exits.
    """
    async with Session(session_id=session_id, type="standard", delete=False) as session:
        print(f"Retrieved session with ID: {session.id}")
        return session

async def get_existing_session_with_alias(alias: str) -> Session:
    """
    Retrieve a session using its alias - this is often more convenient than using IDs.
    """
    async with Session(alias=alias, type="standard", delete=False) as session:
        print(f"Retrieved session with alias: {alias} (ID: {session.id})")
        return session

async def list_sessions():
    """
    The Manager class provides administrative functions for working with sessions.
    This method lists all sessions in your current namespace.
    """
    async with Manager() as manager:
        # show_in_console=True displays a nicely formatted table in the terminal
        sessions = await manager.list_sessions(show_in_console=True)
        return sessions

async def cleanup_namespace() -> None:
    """
    Remove all sessions in your current namespace.
    Useful for cleaning up after testing or when starting a new project.
    """
    async with Manager() as manager:
        await manager.cleanup_namespace()
        print("All sessions in the current namespace have been deleted")

async def delete_session(session_id: str) -> None:
    """
    Delete a specific session by its ID.
    """
    async with Manager() as manager:
        await manager.delete_session(session_id=session_id)
        print(f"Session {session_id} has been deleted")

async def main():
    # Example workflow for session management
    session = await create_session()  # Create a session with custom parameters
    await list_sessions()  # See what sessions exist
    # await cleanup_namespace()  # Uncomment to delete all sessions
    # await delete_session(session_id="YOUR SESSION ID")  # Delete a specific session

if __name__ == "__main__":
    asyncio.run(main())
```

## Querying and Analysis

### Making a Single Query

The most basic way to interact with your documents is through a single query:

```python
# examples/make_single_query.py
import asyncio
import os
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

async def main():
    async with Session(type="standard", delete=True) as session:
        # First, ingest the documents
        await session.ingest(input_dir=input_dir)

        # Then, query the documents
        # The query method searches through your documents and returns relevant information
        # You can customize the response by providing a role for the AI
        await session.query(
            query="¿De qué habla la quinta enmienda de la constitución?",
            # The role parameter influences how the AI responds - here as a Harvard law expert
            role="Eres un abogado experto de harvard",
            display_in_console=True,  # Print the response in the console
        )
        # The response will include relevant passages from the documents and an answer to your question

if __name__ == "__main__":
    asyncio.run(main())
```

### Making Multiple Queries

For more complex analysis, you might want to ask multiple related questions:

```python
# examples/make_multiple_queries.py
import asyncio
import os
from typing import List
from shadai.core.schemas import Query
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

# Define a list of queries to process in sequence
queries: List[Query] = [
    Query(
        query="¿De qué habla la quinta enmienda de la constitución?",
        role="Eres un abogado experto de harvard",
        display_in_console=True,
    ),
    Query(
        query="""
        ¿Cómo se detalla en el Artículo I, Sección 2 el mecanismo de asignación de representantes a
        los estados, y qué implicaciones podría tener la fórmula de prorrateo
        (incluyendo consideraciones como "las tres quintas partes" y la exclusión de indígenas)
        en términos de representación política y distribución de poder?
        """,
        display_in_console=True,
    ),
    # You can add as many queries as needed to analyze different aspects of your documents
]

async def main():
    async with Session(type="standard", delete=True) as session:
        # Ingest documents once
        await session.ingest(input_dir=input_dir)

        # Run all queries in sequence
        # This is more efficient than running separate query calls
        # as the session maintains context between queries
        await session.multiple_queries(queries=queries)
        # Each query and its response will be displayed in the console

if __name__ == "__main__":
    asyncio.run(main())
```

### Getting a Session Summary

SHADAI can generate concise summaries of the documents in your session:

```python
# examples/get_session_summary.py
import asyncio
import os
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

async def main():
    async with Session(type="standard", delete=True) as session:
        # Ingest the documents
        await session.ingest(input_dir=input_dir)

        # Generate a summary of all documents in the session
        # This provides a high-level overview of the key topics and information
        await session.summarize(display_in_console=True)
        # The summary will be displayed in the console and can be used for further analysis

if __name__ == "__main__":
    asyncio.run(main())
```

### Creating an Article

SHADAI can generate comprehensive articles on topics related to the documents in your session:

```python
# examples/create_article.py
import asyncio
import os
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

async def main():
    async with Session(type="standard", delete=True) as session:
        # Ingest the documents
        await session.ingest(input_dir=input_dir)

        # Generate an article on a specific topic
        # This creates a well-structured, detailed piece of content
        # based on information from your documents
        await session.article(
            topic="Enmiendas de la constitución y su impacto social",
            display_in_console=True,
        )
        # The article will be displayed in the console and can be saved or further processed

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Interactions

### Simple LLM Completion

Sometimes you just need a direct answer from the language model:

```python
# examples/call_llm.py
import asyncio
import os
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

async def main():
    async with Session(type="standard", delete=True) as session:
        # Ingest documents to provide context
        await session.ingest(input_dir=input_dir)

        # Use complete for direct language model responses
        # This bypasses the document retrieval step but still considers the document context
        await session.llm_call(
            prompt="¿Cual es el estado con la mayor economía en los Estados Unidos?",
            display_prompt=True,  # Show the prompt in the output
            display_in_console=True,  # Print the response in the console
        )
        # The LLM will generate a response based on its knowledge without document context

if __name__ == "__main__":
    asyncio.run(main())
```

### Chat with Data and History

For interactive conversations that maintain context:

```python
# examples/chat_with_data_and_history.py
import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def chat_with_data_and_history():
    """
    This function chats with the data and history.
    """
    async with Session(type="standard", delete=True) as session:
        await session.ingest(input_dir=input_dir)
        await session.chat(
            message="¿Qué dice la constitución sobre la libertad de expresión?",
            system_prompt="Eres un experto en derecho constitucional y tienes acceso a la constitución.",
            use_history=True,
            display_in_console=True,
        )
        # This is optional to run, it cleans up the chat history
        await session.cleanup_chat()


async def chat_only_with_history():
    """
    This function chats only with the history.
    """
    async with Session(type="standard", delete=True) as session:
        await session.chat(
            message="¿Qué dice la constitución sobre la libertad de expresión?",
            system_prompt="Eres un experto en derecho constitucional y tienes acceso a la constitución.",
            use_history=True,
            display_in_console=True,
        )
        # This is optional to run, it cleans up the chat history
        await session.cleanup_chat()


if __name__ == "__main__":
    asyncio.run(chat_with_data_and_history())
    asyncio.run(chat_only_with_history())
```

### Chat with Images

You can also analyze images using the SHADAI client:

```python
# examples/chat_with_images.py
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
```

### Creating a Tool Agent

For more complex AI-powered workflows, you can create a Tool Agent that combines document knowledge with custom functions:

```python
# examples/create_shadai_agent.py
import asyncio
import os
from typing import Dict
from shadai.core.agents import ToolAgent
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

# Define a function that the agent can use
def get_constitutional_article(article_id: str) -> str:
    """
    This function provides specific information about constitutional amendments.
    The agent can call this function to get detailed information.
    """
    articles: Dict[str, Dict[str, str]] = {
        "1": {
            "title": "Primera Enmienda",
            "description": "Libertad de expresión, religión, prensa y reunión",
            "content": "El Congreso no hará ley alguna con respecto al establecimiento de religión, ni prohibiendo la libre práctica de la misma; ni limitando la libertad de expresión, ni de prensa; ni el derecho del pueblo a reunirse pacíficamente.",
        },
        "2": {
            "title": "Segunda Enmienda",
            "description": "Derecho a portar armas",
            "content": "Siendo necesaria una milicia bien ordenada para la seguridad de un Estado libre, no se violará el derecho del pueblo a poseer y portar armas.",
        },
    }

    if article_id not in articles:
        return "Artículo no encontrado"

    article = articles[article_id]
    return f"Título: {article['title']}\nDescripción: {article['description']}\nContenido: {article['content']}"

async def main():
    async with Session(type="standard", delete=True) as session:
        # Ingest documents to provide context
        await session.ingest(input_dir=input_dir)

        # Create a Tool Agent that combines document knowledge with custom functions
        agent = ToolAgent(
            session=session,
            # Define a prompt template that uses both the function output and document summary
            prompt="""
                Analiza la relación entre la Primera Enmienda y las empresas digitales:

                Enmienda Constitucional:
                {function_output}

                Contexto de documentos:
                {summary}

                Considerando la Primera Enmienda y el contexto histórico, analiza:
                1. Cómo se aplican los principios de libertad de expresión en el entorno digital
                2. Desafíos y oportunidades para las empresas digitales en relación con estos derechos
                3. Recomendaciones para equilibrar la innovación tecnológica con los derechos constitucionales
            """,
            use_summary=True,  # Include document summary in the prompt
            function=get_constitutional_article,  # The function the agent can call
        )

        # Call the agent with specific parameters for the function
        await agent.call(article_id="1")
        # The agent will call the function, get the document summary,
        # and generate a comprehensive analysis based on both information sources

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

The SHADAI client includes comprehensive error handling for:
- Configuration errors
- API communication issues
- File processing problems
- Session management failures

## Author

SHADAI GROUP <jaisir@shadai.ai>
