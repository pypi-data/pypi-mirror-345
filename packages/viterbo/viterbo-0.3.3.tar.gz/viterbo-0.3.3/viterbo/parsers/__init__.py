"""
Language-specific parsers for code analysis.
"""

# Import parsers to make them available
from .python_parser import parse_python_file
from .cpp_parser import parse_cpp_file
from .r_parser import parse_r_file
from .generic_parser import parse_generic_file
