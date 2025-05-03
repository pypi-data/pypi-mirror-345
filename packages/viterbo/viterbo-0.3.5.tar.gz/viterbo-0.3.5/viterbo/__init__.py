"""
Viterbo - A tool for collecting and documenting code for LLM context.

Viterbo helps collect source code files from various languages and
compile them into a readable format for inclusion in LLM prompts.
"""

__version__ = "0.2.0"

# Import primary functions for public API
from .core.collector import document_files, document_python_files
from .core.docstring import extract_docstrings

# Import submodules to make them available
from . import core
from . import parsers
