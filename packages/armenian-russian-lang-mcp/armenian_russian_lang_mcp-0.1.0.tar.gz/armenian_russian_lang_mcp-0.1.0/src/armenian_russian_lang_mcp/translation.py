"""
Translation module for Armenian-Russian and Russian-Armenian translation.

This module provides functionality to translate between Armenian and Russian
using dictionary lookups.
"""

import re

from .transliteration import get_package_resource_path, get_transliterator


class DictionaryEntry:
    """
    A class representing a dictionary entry with translations and metadata.
    """

    def __init__(
        self, word: str, translations: list[str], part_of_speech: str | None,
    ):
        """
        Initialize a dictionary entry.

        Args:
            word: The source word
            translations: List of translations
            part_of_speech: Part of speech (noun, verb, etc.)
        """
        self.word = word
        self.translations = translations
        self.part_of_speech = part_of_speech

    def to_dict(self) -> dict:
        """
        Convert the entry to a dictionary format.

        Returns:
            Dictionary representation of the entry
        """
        return {
            "word": self.word,
            "translations": self.translations,
            "part_of_speech": self.part_of_speech,
        }


class DictionaryParser:
    """
    Parser for DSL format dictionary files.
    """

    def __init__(self):
        """Initialize the dictionary parser."""
        # Regex patterns for parsing DSL files
        self.pos_pattern = re.compile(r"\[i\](.*?[\.з])\[/i\]")

    def parse_dsl_file(self, file_path: str) -> dict[str, DictionaryEntry]:
        """
        Parse a DSL format dictionary file.

        Args:
            file_path: Path to the DSL dictionary file

        Returns:
            Dictionary mapping words to their DictionaryEntry objects
        """
        dictionary = {}
        current_word = None
        current_translations = []
        current_pos = None

        try:
            with open(file_path, encoding="utf-8") as file:
                # Skip header lines starting with #
                for line in file:
                    if line.startswith("#"):
                        continue

                    line = line.strip()  # noqa: PLW2901
                    if not line:
                        continue

                    # If line is not indented, it's a new word
                    if not line.startswith("[m1]"):
                        # Save the previous entry if it exists
                        if current_word:
                            dictionary[current_word] = DictionaryEntry(
                                current_word, current_translations, current_pos,
                            )

                        # Start a new entry
                        current_word = line.lower()
                        current_translations = []
                        current_pos = None
                    else:
                        # This is a translation or metadata for the current word
                        line = line.strip()  # noqa: PLW2901

                        # Check if this line contains part of speech info
                        pos_match = self.pos_pattern.search(line)
                        if pos_match and not current_pos:
                            current_pos = pos_match.group(1)

                        # Check if this is a translation line (usually starts with [m1])
                        if line.startswith("[m1]") and "]" in line:
                            # Extract the translation text
                            translation_text = line.split("]", 1)[1].strip()

                            # Clean up any remaining tags
                            translation_text = re.sub(
                                r"\[p\]\[i\](.*?[\.з])\[/i\]\[/p]", "", translation_text,
                            ).strip()
                            translation_text = re.sub(
                                r"\[/m\]", "", translation_text,
                            ).strip()

                            if translation_text:
                                current_translations.append(translation_text)

                # Don't forget to add the last entry
                if current_word:
                    dictionary[current_word] = DictionaryEntry(
                        current_word, current_translations, current_pos,
                    )

        except Exception as e:
            print(f"Error parsing dictionary file {file_path}: {e}")

        return dictionary


class Translator:
    """
    Translator class for Armenian-Russian and Russian-Armenian translation.
    """

    def __init__(
        self, am_ru_dict_path: str, ru_am_dict_path: str, alphabet_path: str = None,
    ):
        """
        Initialize the translator with dictionary files.

        Args:
            am_ru_dict_path: Path to the Armenian-Russian dictionary file
            ru_am_dict_path: Path to the Russian-Armenian dictionary file
            alphabet_path: Path to the alphabet mapping file
        """
        self.parser = DictionaryParser()
        self.am_ru_dict = self.parser.parse_dsl_file(am_ru_dict_path)
        self.ru_am_dict = self.parser.parse_dsl_file(ru_am_dict_path)
        self.transliterator = get_transliterator(alphabet_path)

    def translate_am_to_ru(self, text: str) -> dict:
        """
        Translate Armenian text to Russian.

        Args:
            text: Armenian text to translate

        Returns:
            Dictionary with translation results
        """
        # Split text into words for dictionary lookup
        words = text.split()
        results = []

        for word in words:
            clean_word = word.strip(".,!?;:()[]{}\"'-")
            lower_word = clean_word.lower()

            if lower_word in self.am_ru_dict:
                entry = self.am_ru_dict[lower_word]
                results.append(
                    {
                        "word": word,
                        "translations": entry.translations,
                        "part_of_speech": entry.part_of_speech,
                        "transliteration": self.transliterator.transliterate(word),
                    },
                )
            else:
                # Fallback to transliteration for unknown words
                results.append(
                    {
                        "word": word,
                        "translations": [],
                        "part_of_speech": None,
                        "transliteration": self.transliterator.transliterate(word),
                    },
                )

        return {"source_text": text, "direction": "am-to-ru", "results": results}

    def translate_ru_to_am(self, text: str) -> dict:
        """
        Translate Russian text to Armenian.

        Args:
            text: Russian text to translate

        Returns:
            Dictionary with translation results
        """
        # Split text into words for dictionary lookup
        words = text.split()
        results = []

        for word in words:
            clean_word = word.strip(".,!?;:()[]{}\"'-")
            lower_word = clean_word.lower()

            if lower_word in self.ru_am_dict:
                entry = self.ru_am_dict[lower_word]
                results.append(
                    {
                        "word": word,
                        "translations": entry.translations,
                        "part_of_speech": entry.part_of_speech,
                        "transliteration": self.transliterator.transliterate(
                            entry.translations[0],
                        ),
                    },
                )
            else:
                # No transliteration fallback for Russian to Armenian
                results.append(
                    {
                        "word": word,
                        "translations": [],
                        "part_of_speech": None,
                        "transliteration": None,
                    },
                )

        return {"source_text": text, "direction": "ru-to-am", "results": results}

    def translate(self, text: str, direction: str = "am-to-ru") -> dict:
        """
        Translate text between Armenian and Russian.

        Args:
            text: Text to translate
            direction: Translation direction ("am-to-ru" or "ru-to-am")

        Returns:
            Dictionary with translation results
        """
        if direction == "am-to-ru":
            return self.translate_am_to_ru(text)
        if direction == "ru-to-am":
            return self.translate_ru_to_am(text)
        raise ValueError(f"Unsupported translation direction: {direction}")


# Create a singleton instance
translator = None


def get_translator(
    am_ru_dict_path: str = None, ru_am_dict_path: str = None, alphabet_path: str = None,
):
    """
    Get or create the translator instance.

    Args:
        am_ru_dict_path: Path to the Armenian-Russian dictionary file. If None, uses the default.
        ru_am_dict_path: Path to the Russian-Armenian dictionary file. If None, uses the default.
        alphabet_path: Path to the alphabet mapping file. If None, uses the default.

    Returns:
        Translator instance
    """
    global translator  # noqa: PLW0603

    if am_ru_dict_path is None:
        am_ru_dict_path = get_package_resource_path("am-rus.dsl")

    if ru_am_dict_path is None:
        ru_am_dict_path = get_package_resource_path("rus-am.dsl")

    if translator is None:
        translator = Translator(am_ru_dict_path, ru_am_dict_path, alphabet_path)
    return translator
