"""
Install the Armenian-Russian Language MCP Server to Claude Desktop.

This script installs the MCP server to Claude Desktop for use with Claude AI.
"""

import inspect
import subprocess
import sys


def main():
    """
    Install the MCP server to Claude Desktop.

    This function is the entry point for the command-line script.
    """
    try:
        # Check if MCP CLI is installed
        subprocess.run(["mcp", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "Error: MCP CLI not found. Please install it with 'pip install \"mcp[cli]\"'",
        )
        sys.exit(1)

    print("Installing Armenian-Russian Language MCP Server to Claude Desktop...")

    try:
        # Get the path to the server module
        from armenian_russian_lang_mcp import server

        server_path = inspect.getfile(server)

        # Install the server to Claude Desktop
        subprocess.run(
            [
                "mcp",
                "install",
                server_path,
                "--name",
                "Armenian-Russian Language Tools",
            ],
            check=True,
        )

        print("\nServer installed successfully!")
        print("You can now use the Armenian-Russian Language Tools in Claude Desktop.")
        print("The following tools are available:")
        print("  - transliterate: Transliterate Armenian text to Russian characters")
        print("  - translate: Translate between Armenian and Russian")
        print("  - batch_translate: Translate multiple words at once")
        print("\nThe following resources are available:")
        print("  - dictionary://am-ru/{word}: Get Armenian-Russian dictionary entry")
        print("  - dictionary://ru-am/{word}: Get Russian-Armenian dictionary entry")

    except subprocess.CalledProcessError as e:
        print(f"Error installing server: {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"Error importing server module: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
