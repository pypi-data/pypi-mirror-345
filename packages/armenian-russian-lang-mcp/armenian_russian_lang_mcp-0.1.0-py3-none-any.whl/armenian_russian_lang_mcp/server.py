"""
Armenian-Russian Language MCP Server

This server provides tools for transliteration and translation between Armenian and Russian.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

from .translation import get_translator
from .transliteration import get_package_resource_path, get_transliterator


@dataclass
class AppContext:
    """Application context for the MCP server."""

    alphabet_path: str
    am_ru_dict_path: str
    ru_am_dict_path: str


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:  # noqa: ARG001
    """
    Manage application lifecycle with type-safe context.

    Args:
        server: The FastMCP server instance

    Yields:
        AppContext: The application context
    """
    # Initialize resources on startup
    alphabet_path = get_package_resource_path("alphabet.md")
    am_ru_dict_path = get_package_resource_path("am-rus.dsl")
    ru_am_dict_path = get_package_resource_path("rus-am.dsl")

    # Pre-initialize the transliterator and translator
    get_transliterator(alphabet_path)
    get_translator(am_ru_dict_path, ru_am_dict_path, alphabet_path)

    print("Initialized Armenian-Russian Language Tools with:")
    print(f"  - Alphabet: {alphabet_path}")
    print(f"  - Armenian-Russian Dictionary: {am_ru_dict_path}")
    print(f"  - Russian-Armenian Dictionary: {ru_am_dict_path}")

    try:
        yield AppContext(
            alphabet_path=alphabet_path,
            am_ru_dict_path=am_ru_dict_path,
            ru_am_dict_path=ru_am_dict_path,
        )
    finally:
        # Cleanup on shutdown (if needed)
        print("Shutting down Armenian-Russian Language Tools")


# Create an MCP server with lifespan management
mcp = FastMCP("Armenian-Russian Language Tools", lifespan=app_lifespan)


# Transliteration tool
@mcp.tool()
def transliterate(text: str) -> dict:
    """
    Transliterate Armenian text to Russian characters.

    Args:
        text: Armenian text to transliterate

    Returns:
        Dictionary with the original text and its transliteration
    """
    transliterator = get_transliterator()
    transliterated_text = transliterator.transliterate(text)

    return {"source_text": text, "transliterated_text": transliterated_text}


# Translation tool
@mcp.tool()
def translate(text: str, direction: str = "am-to-ru") -> dict:
    """
    Translate between Armenian and Russian.

    Args:
        text: Text to translate
        direction: Translation direction ("am-to-ru" or "ru-to-am")

    Returns:
        Dictionary with translation results
    """
    translator = get_translator()
    return translator.translate(text, direction)


# Dictionary lookup resource
@mcp.resource("dictionary://am-ru/{word}")
def get_am_ru_entry(word: str) -> str:
    """
    Get Armenian-Russian dictionary entry.

    Args:
        word: Armenian word to look up

    Returns:
        Dictionary entry as formatted text
    """
    translator = get_translator()

    if word.lower() in translator.am_ru_dict:
        entry = translator.am_ru_dict[word.lower()]

        # Format the entry as text
        result = f"Word: {word}\n"
        if entry.part_of_speech:
            result += f"Part of speech: {entry.part_of_speech}\n"

        result += "Translations:\n"
        for i, translation in enumerate(entry.translations, 1):
            result += f"  {i}. {translation}\n"

        # Add transliteration
        transliterator = get_transliterator()
        result += f"Transliteration: {transliterator.transliterate(word)}"

        return result
    return f"Word '{word}' not found in Armenian-Russian dictionary."


@mcp.resource("dictionary://ru-am/{word}")
def get_ru_am_entry(word: str) -> str:
    """
    Get Russian-Armenian dictionary entry.

    Args:
        word: Russian word to look up

    Returns:
        Dictionary entry as formatted text
    """
    translator = get_translator()

    if word.lower() in translator.ru_am_dict:
        entry = translator.ru_am_dict[word.lower()]

        # Format the entry as text
        result = f"Word: {word}\n"
        if entry.part_of_speech:
            result += f"Part of speech: {entry.part_of_speech}\n"

        result += "Translations:\n"
        for i, translation in enumerate(entry.translations, 1):
            result += f"  {i}. {translation}\n"

        return result
    return f"Word '{word}' not found in Russian-Armenian dictionary."


# Batch translation tool for processing multiple words
@mcp.tool()
def batch_translate(words: list[str], direction: str = "am-to-ru") -> dict:
    """
    Translate a batch of words between Armenian and Russian.

    Args:
        words: List of words to translate
        direction: Translation direction ("am-to-ru" or "ru-to-am")

    Returns:
        Dictionary with translation results for each word
    """
    translator = get_translator()
    results = []

    for word in words:
        if direction == "am-to-ru":
            result = translator.translate_am_to_ru(word)
        else:
            result = translator.translate_ru_to_am(word)
        results.append(result)

    return {"direction": direction, "results": results}


def main():
    """
    Run the MCP server.

    This function is the entry point for the command-line script.
    """
    print("Starting Armenian-Russian Language MCP Server...")
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
