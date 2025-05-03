"""
Formatters for generating output in different file formats.
"""

from datetime import datetime
from pathlib import Path


class BaseFormatter:
    """Base class for formatters"""

    def __init__(self, output_file, source_path):
        """
        Initialize the formatter.

        Args:
            output_file: Path to the output file or "clipboard"
            source_path: Path to a source directory/file or list of paths
        """
        self.output_file = output_file

        # Handle multiple source paths
        if isinstance(source_path, list):
            self.source_paths = source_path
            # Use the first path for display if needed
            self.source_path = source_path[0] if source_path else Path(".")
        else:
            self.source_path = source_path
            self.source_paths = [source_path]

        self.file_count = 0

    def write_header(self, out_file):
        """Write the header to the output file"""
        raise NotImplementedError("Subclasses must implement write_header")

    def write_directory_structure(self, out_file, dir_structure):
        """Write the directory structure to the output file"""
        raise NotImplementedError("Subclasses must implement write_directory_structure")

    def write_file_header(self, out_file, rel_path):
        """Write a file section header to the output file"""
        raise NotImplementedError("Subclasses must implement write_file_header")

    def write_module_docstring(self, out_file, docstring):
        """Write a module docstring to the output file"""
        raise NotImplementedError("Subclasses must implement write_module_docstring")

    def write_code(self, out_file, content, add_line_numbers=False):
        """Write code content to the output file"""
        raise NotImplementedError("Subclasses must implement write_code")

    def write_docstrings(self, out_file, docstrings):
        """Write extracted docstrings to the output file"""
        raise NotImplementedError("Subclasses must implement write_docstrings")

    def write_summary(self, out_file, language_stats):
        """Write the summary to the output file"""
        raise NotImplementedError("Subclasses must implement write_summary")


class TextFormatter(BaseFormatter):
    """Formatter for plain text output"""

    def write_header(self, out_file):
        """Write the header to the output file"""
        out_file.write(f"# Code Documentation\n")
        out_file.write(
            f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        # Handle display of multiple source paths
        if len(self.source_paths) == 1:
            out_file.write(f"# Source: {self.source_paths[0]}\n\n")
        else:
            out_file.write(f"# Sources: {len(self.source_paths)} directories/files\n")
            for i, path in enumerate(self.source_paths):
                out_file.write(f"#   {i+1}. {path}\n")
            out_file.write("\n")

    def write_directory_structure(self, out_file, dir_structure):
        """Write the directory structure to the output file"""
        out_file.write(f"# Directory Structure:\n")
        out_file.write(dir_structure)
        out_file.write("\n\n")

    def write_file_header(self, out_file, rel_path):
        """Write a file section header to the output file"""
        out_file.write(f"\n\n{'=' * 80}\n")
        out_file.write(f"FILE: {rel_path}\n")
        out_file.write(f"{'=' * 80}\n\n")

    def write_module_docstring(self, out_file, docstring):
        """Write a module docstring to the output file"""
        out_file.write("MODULE DOCSTRING:\n")
        out_file.write(f"{docstring}\n\n")

    def write_code(self, out_file, content, add_line_numbers=False):
        """Write code content to the output file"""
        out_file.write("CODE:\n")
        if add_line_numbers:
            for i, line in enumerate(content.splitlines(), 1):
                out_file.write(f"{i:4d} | {line}\n")
        else:
            out_file.write(content)
            if not content.endswith("\n"):
                out_file.write("\n")

    def write_docstrings(self, out_file, docstrings):
        """Write extracted docstrings to the output file"""
        out_file.write("\nDOCSTRINGS:\n")
        for name, doc in sorted(docstrings.items()):
            if name != "module" and name != "file":  # Skip module/file docstring
                out_file.write(f"\n{name}:\n")
                out_file.write(f"{'-' * len(name)}\n")
                out_file.write(f"{doc}\n")

    def write_summary(self, out_file, language_stats):
        """Write the summary to the output file"""
        out_file.write(f"\n\n{'=' * 80}\n")
        total_files = sum(language_stats.values())

        # Adjust summary wording based on single vs. multiple sources
        if len(self.source_paths) == 1:
            out_file.write(
                f"SUMMARY: Documented {total_files} files from {self.source_paths[0]}\n"
            )
        else:
            out_file.write(
                f"SUMMARY: Documented {total_files} files from {len(self.source_paths)} sources\n"
            )

        # Write language-specific stats
        if len(language_stats) > 1:  # Only if there's more than one language
            out_file.write("\nFiles by language:\n")
            for lang, count in sorted(
                language_stats.items(), key=lambda x: x[1], reverse=True
            ):
                out_file.write(f"- {lang}: {count}\n")


class MarkdownFormatter(BaseFormatter):
    """Formatter for Markdown output"""

    def write_header(self, out_file):
        """Write the header to the output file"""
        out_file.write(f"# Code Documentation\n\n")
        out_file.write(
            f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

        # Handle display of multiple source paths
        if len(self.source_paths) == 1:
            out_file.write(f"**Source:** `{self.source_paths[0]}`\n\n")
        else:
            out_file.write(
                f"**Sources:** {len(self.source_paths)} directories/files\n\n"
            )
            for i, path in enumerate(self.source_paths):
                out_file.write(f"{i+1}. `{path}`\n")
            out_file.write("\n")

    def write_directory_structure(self, out_file, dir_structure):
        """Write the directory structure to the output file"""
        out_file.write(f"## Directory Structure\n\n")
        out_file.write("```\n")
        out_file.write(dir_structure)
        out_file.write("\n```\n\n")

    def write_file_header(self, out_file, rel_path):
        """Write a file section header to the output file"""
        out_file.write(f"\n## {rel_path}\n\n")

    def write_module_docstring(self, out_file, docstring):
        """Write a module docstring to the output file"""
        out_file.write("### Module Documentation\n\n")
        out_file.write("> " + docstring.replace('\n', '\n> ') + "\n\n")

    def write_code(self, out_file, content, add_line_numbers=False, language=None):
        """Write code content to the output file"""
        out_file.write("### Code\n\n")

        # Determine the language for syntax highlighting
        lang_str = f"```{language.lower() if language else ''}"
        out_file.write(lang_str + "\n")

        if add_line_numbers:
            for i, line in enumerate(content.splitlines(), 1):
                out_file.write(f"{i:4d} | {line}\n")
        else:
            out_file.write(content)
            if not content.endswith("\n"):
                out_file.write("\n")

        out_file.write("```\n\n")

    def write_docstrings(self, out_file, docstrings):
        """Write extracted docstrings to the output file"""
        if len(docstrings) > 1 or (
            "module" not in docstrings and "file" not in docstrings
        ):
            out_file.write("### Documentation\n\n")

            for name, doc in sorted(docstrings.items()):
                if name != "module" and name != "file":  # Skip module/file docstring
                    out_file.write(f"#### {name}\n\n")
                    out_file.write(f"{doc}\n\n")

    def write_summary(self, out_file, language_stats):
        """Write the summary to the output file"""
        out_file.write(f"## Summary\n\n")
        total_files = sum(language_stats.values())

        # Adjust summary wording based on single vs. multiple sources
        if len(self.source_paths) == 1:
            out_file.write(
                f"Documented **{total_files}** files from `{self.source_paths[0]}`\n\n"
            )
        else:
            out_file.write(
                f"Documented **{total_files}** files from **{len(self.source_paths)}** sources\n\n"
            )

        # Write language-specific stats
        if len(language_stats) > 1:  # Only if there's more than one language
            out_file.write("### Files by language\n\n")
            out_file.write("| Language | Count |\n")
            out_file.write("|----------|-------|\n")
            for lang, count in sorted(
                language_stats.items(), key=lambda x: x[1], reverse=True
            ):
                out_file.write(f"| {lang} | {count} |\n")


def get_formatter(output_format, output_file, source_path):
    """
    Factory function to create the appropriate formatter.

    Args:
        output_format: Format of the output ('txt' or 'md')
        output_file: Path to the output file or "clipboard"
        source_path: Path or list of paths to the source(s)

    Returns:
        Formatter instance
    """
    if output_format.lower() == "md":
        return MarkdownFormatter(output_file, source_path)
    else:
        return TextFormatter(output_file, source_path)
