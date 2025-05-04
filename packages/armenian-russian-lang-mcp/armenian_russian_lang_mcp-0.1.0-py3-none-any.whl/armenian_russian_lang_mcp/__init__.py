"""
Armenian-Russian Language Tools with MCP support.

This package provides tools for transliteration and translation between Armenian and Russian languages.
"""

from .translation import get_translator
from .transliteration import get_transliterator

__version__ = "0.1.0"


def transliterate(text: str) -> str:
    """
    Transliterate Armenian text to Russian.

    Args:
        text: Armenian text to transliterate

    Returns:
        Transliterated text in Russian
    """
    transliterator = get_transliterator()
    return transliterator.transliterate(text)


def translate(text: str, direction: str = "am-to-ru") -> dict:
    """
    Translate text between Armenian and Russian.

    Args:
        text: Text to translate
        direction: Translation direction ("am-to-ru" or "ru-to-am")

    Returns:
        Dictionary with translation results
    """
    translator = get_translator()
    return translator.translate(text, direction)
