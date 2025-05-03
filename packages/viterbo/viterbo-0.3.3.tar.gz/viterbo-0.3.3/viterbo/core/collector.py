"""
Core functionality for collecting and documenting code files.
"""

import sys
import os
from pathlib import Path
from collections import defaultdict
import io

from .docstring import extract_docstrings
from .formatter import get_formatter
from .utils import (
    generate_directory_structure,
    get_language_from_extension,
    is_binary_file,
    copy_to_clipboard,
)


def document_files(
    source_paths,
    output_file=None,
    file_extensions=None,
    include_readme=False,
    include_docstrings=False,
    add_line_numbers=False,
    output_format="txt",
):
    """
    Process code files from multiple sources and generate documentation.

    Args:
        source_paths: List of directories and/or files to process, or a single path
        output_file: Output file to write documentation, or None to copy to clipboard
        file_extensions: List of file extensions to include (default: ['.py'])
        include_readme: Whether to include README.md files
        include_docstrings: Whether to extract and include docstrings from code files
        add_line_numbers: Whether to add line numbers to code
        output_format: Output format, either 'txt' or 'md'

    Returns:
        Boolean indicating success
    """
    try:
        # Handle single string input for backward compatibility
        if isinstance(source_paths, (str, Path)):
            source_paths = [source_paths]

        # Set default file extensions if not provided
        if file_extensions is None:
            file_extensions = [".py"]

        # Ensure all file extensions are strings with leading dots
        clean_extensions = []
        for ext in file_extensions:
            ext_str = str(ext)
            if not ext_str.startswith("."):
                ext_str = f".{ext_str}"
            clean_extensions.append(ext_str)

        file_extensions = clean_extensions

        # Collect and validate all source paths
        valid_paths = []
        for source in source_paths:
            # Convert to absolute path
            source_path = Path(source).resolve()

            # Check if path exists
            if not source_path.exists():
                print(
                    f"Warning: Source '{source}' does not exist, skipping",
                    file=sys.stderr,
                )
                continue

            # Check permissions
            try:
                if source_path.is_dir():
                    next(source_path.iterdir(), None)  # Test read permission
                else:
                    # For files, try to open and close it to check read permission
                    with open(source_path, "r", encoding="utf-8", errors="ignore"):
                        pass
            except PermissionError:
                print(
                    f"Warning: Permission denied when accessing '{source}', skipping",
                    file=sys.stderr,
                )
                continue

            valid_paths.append(source_path)

        # Ensure we have at least one valid source
        if not valid_paths:
            print("Error: No valid source paths provided", file=sys.stderr)
            return False

        # Create formatter based on output format
        formatter = get_formatter(
            output_format, output_file or "clipboard", valid_paths[0]
        )

        # Determine if we're writing to a file or to clipboard
        use_clipboard = output_file is None

        # If using clipboard, create a StringIO object to collect the output
        if use_clipboard:
            out_buffer = io.StringIO()
            out = out_buffer
        else:
            # Create or clear the output file
            try:
                out = open(output_file, "w", encoding="utf-8")
            except PermissionError:
                print(
                    f"Error: Permission denied when writing to output file '{output_file}'",
                    file=sys.stderr,
                )
                return False

        try:
            # Write header
            formatter.write_header(out)

            # Generate and write directory structure for all sources
            dir_structure = generate_directory_structure(
                valid_paths, file_extensions, include_readme
            )
            formatter.write_directory_structure(out, dir_structure)

            # Find all relevant files
            all_files = []

            # Process source paths (files and directories)
            for source_path in valid_paths:
                if source_path.is_dir():
                    # For directories, collect matching files recursively
                    directory_files = []

                    # Collect code files
                    for ext in file_extensions:
                        try:
                            ext_str = str(ext)
                            found_files = sorted(source_path.glob(f"**/*{ext_str}"))
                            directory_files.extend(found_files)
                        except PermissionError:
                            print(
                                f"Error: Permission denied when reading {ext} files in '{source_path}'",
                                file=sys.stderr,
                            )

                    # Add README files if requested
                    if include_readme:
                        try:
                            readme_files = sorted(source_path.glob("**/README.md"))
                            directory_files.extend(readme_files)
                        except PermissionError:
                            print(
                                f"Error: Permission denied when reading README.md files in '{source_path}'",
                                file=sys.stderr,
                            )

                    all_files.extend(directory_files)
                else:
                    # For individual files, add them if they match our extensions or are README files
                    if any(
                        str(source_path.name).endswith(ext) for ext in file_extensions
                    ) or (include_readme and source_path.name.lower() == "readme.md"):
                        all_files.append(source_path)

            # De-duplicate files (in case of nested directories or files specified explicitly)
            all_files = sorted(set(all_files), key=lambda x: str(x))

            language_stats = defaultdict(int)

            for file_path in all_files:
                try:
                    # Get the relative path for display - try to make it relative to one of our source directories
                    rel_path = None
                    for source_path in valid_paths:
                        if source_path.is_dir() and str(file_path).startswith(
                            str(source_path)
                        ):
                            try:
                                rel_path = file_path.relative_to(source_path)
                                break
                            except ValueError:
                                pass

                    # If we couldn't get a relative path, use the filename
                    if rel_path is None:
                        rel_path = file_path.name

                    # Skip binary files
                    if is_binary_file(file_path):
                        print(f"Skipping binary file: {rel_path}", file=sys.stderr)
                        continue

                    # Determine language based on file extension
                    file_ext = str(file_path.suffix)
                    language = get_language_from_extension(file_ext)
                    language_stats[language] += 1

                    # Write file header
                    formatter.write_file_header(out, rel_path)

                    # Extract docstrings if requested
                    docstrings = {}
                    if include_docstrings:
                        docstrings = extract_docstrings(file_path)

                        # Write module docstring if present
                        if "module" in docstrings:
                            formatter.write_module_docstring(out, docstrings["module"])
                        elif "file" in docstrings:
                            formatter.write_module_docstring(out, docstrings["file"])

                    # Write file content with optional line numbers
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if output_format.lower() == "md":
                                formatter.write_code(
                                    out, content, add_line_numbers, language
                                )
                            else:
                                formatter.write_code(out, content, add_line_numbers)

                    except UnicodeDecodeError:
                        # Try with a different encoding
                        try:
                            with open(file_path, "r", encoding="latin-1") as f:
                                content = f.read()
                                if output_format.lower() == "md":
                                    formatter.write_code(
                                        out, content, add_line_numbers, language
                                    )
                                else:
                                    formatter.write_code(out, content, add_line_numbers)
                        except Exception as e:
                            out.write(
                                f"Error reading file with alternate encoding: {e}\n"
                            )
                    except PermissionError:
                        out.write(
                            f"Error: Permission denied when reading file {file_path}\n"
                        )
                    except Exception as e:
                        out.write(f"Error reading file: {e}\n")

                    # Write extracted docstrings
                    if include_docstrings and docstrings:
                        # Check if we have non-module docstrings
                        non_module_docstrings = {
                            k: v
                            for k, v in docstrings.items()
                            if k not in ["module", "file"]
                        }
                        if non_module_docstrings:
                            formatter.write_docstrings(out, docstrings)

                except PermissionError:
                    print(
                        f"Skipping file {file_path} due to permission error",
                        file=sys.stderr,
                    )
                    continue
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}", file=sys.stderr)
                    continue

            # Write summary
            formatter.write_summary(out, language_stats)

            # Handle clipboard output or close the file
            if use_clipboard:
                clipboard_content = out_buffer.getvalue()
                clipboard_success = copy_to_clipboard(clipboard_content)

                if clipboard_success:
                    print(
                        f"Documentation copied to clipboard! {sum(language_stats.values())} files documented"
                    )
                else:
                    print(
                        "Failed to copy to clipboard. Consider specifying an output file instead."
                    )
                    return False
            else:
                out.close()
                print(
                    f"Documentation complete! {sum(language_stats.values())} files documented in '{output_file}'"
                )

            # Print language breakdown if multiple languages
            if len(language_stats) > 1:
                print("\nFiles by language:")
                for lang, count in sorted(
                    language_stats.items(), key=lambda x: x[1], reverse=True
                ):
                    print(f"- {lang}: {count}")

            return True

        finally:
            # Make sure we close the file if it's open
            if not use_clipboard and "out" in locals() and not out.closed:
                out.close()

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


def document_python_files(
    source_paths, output_file=None, include_docstrings=False, add_line_numbers=False
):
    """
    Legacy wrapper for document_files that only processes Python files.

    Args:
        source_paths: List of directories and/or files to process, or a single path
        output_file: Output file to write documentation, or None to copy to clipboard
        include_docstrings: Whether to extract and include docstrings
        add_line_numbers: Whether to add line numbers to code

    Returns:
        Boolean indicating success
    """
    return document_files(
        source_paths=source_paths,
        output_file=output_file,
        file_extensions=[".py"],
        include_readme=False,
        include_docstrings=include_docstrings,
        add_line_numbers=add_line_numbers,
        output_format="txt",
    )
