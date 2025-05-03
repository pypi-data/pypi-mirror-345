"""
Command-line interface for Viterbo.

This module provides the command-line interface for the Viterbo tool, which collects
and documents code files for inclusion in LLM context. The CLI supports:

- Processing multiple directories and files as input sources
- Handling multiple programming languages (Python, C/C++, JavaScript, etc.)
- Extracting docstrings and comments from code
- Generating output in text or markdown format
- Copying output to clipboard when no output file is specified
- Including README files and directory structure visualization

Usage examples:
    # Copy Python files documentation from current dir to clipboard
    viterbo .

    # Document specific files and save to output.txt
    viterbo main.py utils.py config.py output.txt

    # Document multiple directories and files
    viterbo src/ tests/ config.py output.md --format md

    # Document multiple sources with docstrings in markdown format
    viterbo src/ lib/ main.py docs.md --extensions .py .js .cpp --include-docstrings --format md
"""

import argparse
import sys
from pathlib import Path
from .core.collector import document_files


def main():
    """
    Main entry point for the CLI.

    Parses command-line arguments, validates input, and calls the document_files
    function with appropriate parameters. The function supports:

    - Multiple input sources (files and/or directories)
    - File output: When an output_file is specified, writes documentation to that file
    - Clipboard output: When no output_file is provided, copies output to clipboard

    Returns:
        int: 0 for success, 1 for errors
    """
    # Create argument parser with description
    parser = argparse.ArgumentParser(
        description="Document code files from directories and/or files into a consolidated file or clipboard"
    )

    # Required and positional arguments
    parser.add_argument(
        "sources",
        nargs="+",  # Accept one or more input sources
        help="Source directories and/or files to document",
    )

    # File selection options group
    file_group = parser.add_argument_group("File Selection")
    file_group.add_argument(
        "--extensions",
        nargs="+",
        default=[".py"],
        help="File extensions to include (e.g., .py .cpp .r)",
    )
    file_group.add_argument(
        "--include-readme",
        action="store_true",
        help="Include README.md files in the documentation",
    )

    # Content options group
    content_group = parser.add_argument_group("Content Options")
    content_group.add_argument(
        "--include-docstrings",
        action="store_true",
        help="Extract and include docstrings and comments",
    )
    content_group.add_argument(
        "--add-line-numbers", action="store_true", help="Add line numbers to the code"
    )

    # Output options group
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--format",
        choices=["txt", "md"],
        default="txt",
        help="Output format: text or markdown",
    )
    output_group.add_argument(
        "--output-file",
        "-o",
        default=None,
        help="Output file to write documentation (if omitted, output is copied to clipboard)",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Separate sources and check if the last argument might be an output file
    sources = args.sources
    output_file = args.output_file

    # If no explicit output file is given with -o/--output-file, check if the last positional argument
    # might be an output file (for backward compatibility with old command format)
    if output_file is None and len(sources) > 1:
        # Check if the last source has an extension that doesn't match our target extensions
        # and isn't a directory - if so, it's likely intended as an output file
        last_source = Path(sources[-1])

        # Normalize file extensions to include the dot if missing
        extensions = []
        for ext in args.extensions:
            ext_str = str(ext)
            if not ext_str.startswith("."):
                ext_str = f".{ext_str}"
            extensions.append(ext_str)

        # If the last source has an extension that's not in our target list and isn't a directory,
        # treat it as the output file
        if (
            not last_source.is_dir()
            and last_source.suffix
            and last_source.suffix.lower() not in extensions
        ):
            output_file = sources.pop()

    # Normalize file extensions to include the dot if missing
    extensions = []
    for ext in args.extensions:
        ext_str = str(ext)
        if ext_str.startswith("."):
            extensions.append(ext_str)
        else:
            extensions.append(f".{ext_str}")

    # Call document_files function with parsed arguments
    # If output_file is None, results will be copied to clipboard
    success = document_files(
        source_paths=sources,  # Pass list of sources
        output_file=output_file,  # None means copy to clipboard
        file_extensions=extensions,
        include_readme=args.include_readme,
        include_docstrings=args.include_docstrings,
        add_line_numbers=args.add_line_numbers,
        output_format=args.format,
    )

    # Return appropriate exit code
    if not success:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
