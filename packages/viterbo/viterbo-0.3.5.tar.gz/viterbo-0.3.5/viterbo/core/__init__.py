"""
Core functionality for the Viterbo code collector.
"""

from .collector import document_files
from .docstring import extract_docstrings
from .formatter import get_formatter
from .utils import (
    generate_directory_structure,
    get_language_from_extension,
    is_binary_file,
)
