"""
Utility functions for Viterbo.
"""

import os
from pathlib import Path
import sys


def copy_to_clipboard(text):
    """
    Copy text to system clipboard. Uses pyperclip as a dependency.

    Args:
        text: String to copy to clipboard

    Returns:
        Boolean indicating success
    """
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except ImportError:
        print(
            "Error: pyperclip package is required for clipboard functionality.",
            file=sys.stderr,
        )
        print("Install it with: pip install pyperclip", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error copying to clipboard: {e}", file=sys.stderr)
        return False


def generate_directory_structure(paths, file_extensions, include_readme=False):
    """
    Generate a text representation of the directory structure for multiple paths.

    Args:
        paths: List of Path objects representing files and/or directories
        file_extensions: List of file extensions to include
        include_readme: Whether to include README.md files

    Returns:
        String representation of the directory structure
    """
    result = []

    # Separate directories and files
    directories = [p for p in paths if p.is_dir()]
    files = [p for p in paths if p.is_file()]

    # Process directories
    for directory in directories:
        dir_result = []
        root_path = directory

        def _add_directory(directory, prefix="", is_last=False):
            # Format current directory name
            rel_path = directory.relative_to(root_path)
            dir_name = directory.name if directory != root_path else rel_path

            # Skip hidden directories
            if str(dir_name).startswith(".") and directory != root_path:
                return

            if directory == root_path:
                dir_result.append(f"{dir_name}/")
                new_prefix = ""
            else:
                connector = "└── " if is_last else "├── "
                dir_result.append(f"{prefix}{connector}{dir_name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")

            # Get all items in the directory
            try:
                items = list(directory.iterdir())

                # Filter out hidden files and directories
                items = [item for item in items if not str(item.name).startswith(".")]

                # Sort: directories first, then files
                items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

                # Filter files by extension
                files = [
                    item
                    for item in items
                    if item.is_file()
                    and (
                        any(
                            str(item.name).endswith(str(ext)) for ext in file_extensions
                        )
                        or (include_readme and str(item.name).lower() == "readme.md")
                    )
                ]

                # Get all directories
                dirs = [item for item in items if item.is_dir()]

                # Process files
                for i, file in enumerate(files):
                    is_last_file = i == len(files) - 1 and len(dirs) == 0
                    connector = "└── " if is_last_file else "├── "
                    dir_result.append(f"{new_prefix}{connector}{file.name}")

                # Process directories recursively
                for i, dir_path in enumerate(dirs):
                    is_last_dir = i == len(dirs) - 1
                    _add_directory(dir_path, new_prefix, is_last_dir)

            except PermissionError:
                dir_result.append(f"{new_prefix}├── [Permission Denied]")

        _add_directory(root_path)
        result.extend(dir_result)

        # Add a blank line between directory structures for readability
        if len(directories) > 1 and directory != directories[-1]:
            result.append("")

    # Process individual files (not part of directories)
    if files:
        # Only add a blank line if we've already processed directories
        if directories:
            result.append("")
            result.append("Individual files:")

        # Add files to the result
        for file in files:
            result.append(f"├── {file.name}")

    # Return the complete structure
    return "\n".join(result)


def get_language_from_extension(file_ext):
    """
    Determine the programming language based on file extension.

    Args:
        file_ext: File extension (including the dot)

    Returns:
        String representing the language name
    """
    # Ensure file_ext is a string
    file_ext = str(file_ext)

    extension_map = {
        # Python
        ".py": "Python",
        ".pyw": "Python",
        ".pyx": "Python",
        # C/C++
        ".c": "C",
        ".h": "C",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".hpp": "C++",
        ".hxx": "C++",
        # JavaScript/TypeScript
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        # Web
        ".html": "HTML",
        ".css": "CSS",
        # R
        ".r": "R",
        ".R": "R",
        # Java
        ".java": "Java",
        # Go
        ".go": "Go",
        # Rust
        ".rs": "Rust",
        # Ruby
        ".rb": "Ruby",
        # PHP
        ".php": "PHP",
        # Swift
        ".swift": "Swift",
        # Kotlin
        ".kt": "Kotlin",
        # C#
        ".cs": "C#",
        # Shell scripts
        ".sh": "Shell",
        ".bash": "Shell",
        # Markdown
        ".md": "Markdown",
        # JSON/YAML
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        # SQL
        ".sql": "SQL",
    }

    return extension_map.get(file_ext.lower(), "Unknown")


def is_binary_file(file_path):
    """
    Check if a file is binary (non-text).

    Args:
        file_path: Path to the file

    Returns:
        Boolean indicating if the file is binary
    """
    # Check file extension for common binary formats
    binary_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".tiff",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".o",
        ".obj",
        ".pyc",
        ".pyo",
        ".pyd",
        ".class",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".rar",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    }

    # Ensure we get the suffix as a string
    file_suffix = str(file_path.suffix).lower()
    if file_suffix in binary_extensions:
        return True

    # Try to read the first few bytes to detect binary content
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\0" in chunk  # Binary files typically contain null bytes
    except Exception:
        # If there's an error, assume it's binary to be safe
        return True
