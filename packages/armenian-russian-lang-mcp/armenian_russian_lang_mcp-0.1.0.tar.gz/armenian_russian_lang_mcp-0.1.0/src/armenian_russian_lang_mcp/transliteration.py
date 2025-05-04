"""
Transliteration module for Armenian to Russian conversion.

This module provides functionality to convert Armenian text to Russian characters
based on pronunciation rules.
"""

import os


def get_package_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a package resource file.

    Args:
        relative_path: Relative path to the resource file

    Returns:
        Absolute path to the resource file
    """
    package_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(package_dir, relative_path)


class ArmenianToRussianTransliterator:
    """
    A class to handle transliteration from Armenian to Russian.
    """

    def __init__(self, alphabet_file_path: str):
        """
        Initialize the transliterator with the alphabet mapping file.

        Args:
            alphabet_file_path: Path to the alphabet mapping file (MD format)
        """
        self.char_map = self._load_alphabet_mapping(alphabet_file_path)

    def _load_alphabet_mapping(self, file_path: str) -> dict[str, str]:
        """
        Load the Armenian to Russian character mapping from the alphabet file.

        Args:
            file_path: Path to the alphabet mapping file

        Returns:
            Dictionary mapping Armenian characters to Russian transliterations
        """
        char_map = {}

        try:
            with open(file_path, encoding="utf-8") as file:
                # Skip the header line
                next(file)

                for line in file:
                    line = line.strip()  # noqa: PLW2901
                    if not line or "|" not in line:
                        continue

                    # Parse the line in format: | Աա    | [а]          |
                    parts = line.split("|")
                    if len(parts) >= 3:  # noqa: PLR2004
                        armenian_chars = parts[1].strip()
                        russian_trans = parts[2].strip()

                        # Remove the brackets from the transliteration
                        russian_trans = russian_trans.strip("[]")

                        # Handle single and multi-character Armenian letters
                        if len(armenian_chars) == 1:
                            char_map[armenian_chars] = russian_trans
                        elif len(armenian_chars) == 2:  # noqa: PLR2004
                            # For single letters like 'Աա', map both uppercase and lowercase
                            char_map[armenian_chars[0]] = russian_trans  # Uppercase
                            char_map[armenian_chars[1]] = russian_trans  # Lowercase
                        elif " " in armenian_chars:
                            # Handle special cases like 'Ու ու'
                            parts = armenian_chars.split()
                            for part in parts:
                                char_map[part] = russian_trans
                        else:
                            # Handle special characters like 'և'
                            char_map[armenian_chars] = russian_trans

        except Exception as e:
            print(f"Error loading alphabet mapping: {e}")
            # Return an empty map in case of error
            return {}

        return char_map

    def transliterate(self, text: str) -> str:
        """
        Transliterate Armenian text to Russian characters.

        Args:
            text: Armenian text to transliterate

        Returns:
            Transliterated text in Russian characters
        """
        result = ""
        i = 0

        while i < len(text):
            # Check for special two-character combinations first
            if i < len(text) - 1 and text[i : i + 2] in self.char_map:
                result += self.char_map[text[i : i + 2]]
                i += 2
            # Then check for single characters
            elif text[i] in self.char_map:
                result += self.char_map[text[i]]
                i += 1
            # Keep non-Armenian characters as is
            else:
                result += text[i]
                i += 1

        return result


# Create a singleton instance
transliterator = None


def get_transliterator(alphabet_file_path: str = None):
    """
    Get or create the transliterator instance.

    Args:
        alphabet_file_path: Path to the alphabet mapping file. If None, uses the default.

    Returns:
        ArmenianToRussianTransliterator instance
    """
    global transliterator  # noqa: PLW0603

    if alphabet_file_path is None:
        alphabet_file_path = get_package_resource_path("alphabet.md")

    if transliterator is None:
        transliterator = ArmenianToRussianTransliterator(alphabet_file_path)
    return transliterator
