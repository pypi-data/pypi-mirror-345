# Armenian-Russian Language MCP

MCP server and library for transliteration and translation between Armenian and Russian languages.

## Features

- **Transliteration**: Convert Armenian text to Russian characters based on pronunciation rules
- **Bidirectional Translation**: Translate between Armenian and Russian using dictionary lookups
- **Dictionary Resources**: Access dictionary entries for specific words
- **Batch Processing**: Translate multiple words at once
- **MCP Server**: Integration with Claude Desktop and other systems via the MCP protocol

## Installation

```bash
pip install armenian-russian-lang-mcp
```

## Usage

### As a Python Library

```python
from armenian_russian_lang_mcp import transliterate, translate

# Transliterate Armenian text to Russian
result = transliterate("Բարև")
print(result)  # "барев"

# Translate Armenian to Russian
result = translate("աբբա", direction="am-to-ru")
print(result)  # Dictionary with translation results

# Translate Russian to Armenian
result = translate("авва", direction="ru-to-am")
print(result)  # Dictionary with translation results
```

### As an MCP Server

Running the server:

```bash
# Run using the entry point
armenian-russian-mcp-server

# Or using the Python module
python -m armenian_russian_lang_mcp.server
```

#### Available MCP Tools

1. **transliterate**: Transliterate Armenian text to Russian characters
   ```python
   # Example usage
   result = await session.call_tool("transliterate", arguments={"text": "Բարև"})
   ```

2. **translate**: Translate text between Armenian and Russian
   ```python
   # Example usage (Armenian to Russian)
   result = await session.call_tool("translate", arguments={
       "text": "աբբա",
       "direction": "am-to-ru"
   })
   
   # Example usage (Russian to Armenian)
   result = await session.call_tool("translate", arguments={
       "text": "аббат",
       "direction": "ru-to-am"
   })
   ```

3. **batch_translate**: Translate multiple words at once
   ```python
   # Example usage
   result = await session.call_tool("batch_translate", arguments={
       "words": ["աբբա", "աբբահայր"],
       "direction": "am-to-ru"
   })
   ```

#### Available MCP Resources

1. **dictionary://am-ru/{word}**: Get Armenian-Russian dictionary entry
   ```python
   # Example usage
   content, mime_type = await session.read_resource("dictionary://am-ru/աբբա")
   ```

2. **dictionary://ru-am/{word}**: Get Russian-Armenian dictionary entry
   ```python
   # Example usage
   content, mime_type = await session.read_resource("dictionary://ru-am/аббат")
   ```

### Installing in Claude Desktop

To use with Claude Desktop:

```bash
# Run using the entry point
armenian-russian-mcp-install-to-claude

# Or using the Python module
python -m armenian_russian_lang_mcp.install_to_claude
```

## Project Structure

- **Core Components**:
  - `server.py`: MCP server implementation
  - `transliteration.py`: Armenian to Russian transliteration module
  - `translation.py`: Bidirectional translation module

- **Resource Files**:
  - `alphabet.md`: Armenian alphabet with Russian transliteration rules
  - `am-rus.dsl`: Armenian-Russian dictionary
  - `rus-am.dsl`: Russian-Armenian dictionary

## Development

### Cloning the Repository

```bash
git clone https://gitlab.com/smoug25/armenian-russian-lang-mcp.git
cd armenian-russian-lang-mcp
```

### Installing in Development Mode

```bash
pip install -e .
```

### Running Tests

```bash
# Run all tests
make test

```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
