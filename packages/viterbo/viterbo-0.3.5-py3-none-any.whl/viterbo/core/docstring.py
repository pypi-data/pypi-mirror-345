"""
Functionality for extracting documentation from source code files.
"""

import ast
import re
import sys


def extract_python_docstrings(file_path):
    """
    Extract docstrings from a Python file using the ast module.

    Args:
        file_path: Path to the Python file

    Returns:
        Dictionary mapping names to docstrings
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            source = file.read()

        parsed = ast.parse(source)
        docstrings = {}

        # Module docstring
        if (
            len(parsed.body) > 0
            and isinstance(parsed.body[0], ast.Expr)
            and isinstance(parsed.body[0].value, ast.Constant)
            and isinstance(parsed.body[0].value.value, str)
        ):
            docstrings["module"] = parsed.body[0].value.value.strip()
        # Handle older Python versions
        elif (
            len(parsed.body) > 0
            and isinstance(parsed.body[0], ast.Expr)
            and isinstance(parsed.body[0].value, ast.Str)
        ):
            docstrings["module"] = parsed.body[0].value.s.strip()

        # Function and class docstrings
        for node in ast.walk(parsed):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings[node.name] = doc.strip()

        return docstrings
    except Exception as e:
        print(f"Error extracting docstrings from {file_path}: {e}", file=sys.stderr)
        return {}


def extract_cpp_comments(file_path):
    """
    Extract documentation comments from C/C++ files.

    Args:
        file_path: Path to the C/C++ file

    Returns:
        Dictionary mapping function/class names to comments
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Dictionary to store comments
        comments = {}

        # Extract file-level comment at the top (if exists)
        file_comment_match = re.search(r"^\s*/\*\*(.*?)\*/\s*", content, re.DOTALL)
        if file_comment_match:
            file_comment = file_comment_match.group(1).strip()
            comments["file"] = re.sub(r"\n\s*\*\s*", "\n", file_comment)

        # Extract function/class documentation
        # Pattern for function/class definitions with preceding comments
        pattern = r"/\*\*(.*?)\*/\s*(?:template\s*<.*>)?\s*(class|struct|enum|typename|namespace|inline|static|virtual|explicit|constexpr|auto|void|int|float|double|bool|char|unsigned|signed|long|short|size_t|std::.*?|[\w_]+::[\w_]+|[\w_]+)\s+([\w_]+)\s*(?:\(|\{|:|::|<)"

        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            comment = match.group(1).strip()
            identifier_type = match.group(2).strip()
            identifier_name = match.group(3).strip()

            # Clean up comment (remove * at beginning of lines)
            comment = re.sub(r"\n\s*\*\s*", "\n", comment)

            comments[identifier_name] = comment

        return comments
    except Exception as e:
        print(f"Error extracting comments from {file_path}: {e}", file=sys.stderr)
        return {}


def extract_r_comments(file_path):
    """
    Extract documentation comments from R files.

    Args:
        file_path: Path to the R file

    Returns:
        Dictionary mapping function names to comments
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Dictionary to store comments
        comments = {}

        # Extract file-level Roxygen comment at the top (if exists)
        file_comment_match = re.search(r"^\s*#\'(.*?)(?=\n[^#\'])", content, re.DOTALL)
        if file_comment_match:
            file_comment = file_comment_match.group(1).strip()
            comments["file"] = re.sub(r"\n\s*#\'\s*", "\n", file_comment)

        # Extract function documentation (Roxygen style)
        # Pattern for R function definitions with preceding comments
        pattern = r"(#\'.*?)(?=\n[^#\'])\s*([\w_.]+)\s*<-\s*function\s*\("

        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            comment = match.group(1).strip()
            function_name = match.group(2).strip()

            # Clean up comment (remove #' at beginning of lines)
            comment = re.sub(r"\n\s*#\'\s*", "\n", comment.replace("#'", "", 1))

            comments[function_name] = comment

        return comments
    except Exception as e:
        print(f"Error extracting comments from {file_path}: {e}", file=sys.stderr)
        return {}


def extract_js_comments(file_path):
    """
    Extract documentation comments from JavaScript/TypeScript files.

    Args:
        file_path: Path to the JS/TS file

    Returns:
        Dictionary mapping function/class names to comments
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Dictionary to store comments
        comments = {}

        # Extract file-level JSDoc comment
        file_comment_match = re.search(r"^\s*/\*\*(.*?)\*/\s*", content, re.DOTALL)
        if file_comment_match:
            file_comment = file_comment_match.group(1).strip()
            comments["file"] = re.sub(r"\n\s*\*\s*", "\n", file_comment)

        # Extract function/class/method documentation using JSDoc
        pattern = r"/\*\*(.*?)\*/\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(function|class|const|let|var|interface|type|enum)\s+([\w_$]+)"

        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            comment = match.group(1).strip()
            identifier_type = match.group(2).strip()
            identifier_name = match.group(3).strip()

            # Clean up comment (remove * at beginning of lines)
            comment = re.sub(r"\n\s*\*\s*", "\n", comment)

            comments[identifier_name] = comment

        return comments
    except Exception as e:
        print(f"Error extracting comments from {file_path}: {e}", file=sys.stderr)
        return {}


def extract_docstrings(file_path):
    """
    Extract documentation from a file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary mapping names to documentation
    """
    ext = str(file_path.suffix).lower()

    if ext in [".py", ".pyw", ".pyx"]:
        return extract_python_docstrings(file_path)
    elif ext in [".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hxx"]:
        return extract_cpp_comments(file_path)
    elif ext in [".r", ".R"]:
        return extract_r_comments(file_path)
    elif ext in [".js", ".jsx", ".ts", ".tsx"]:
        return extract_js_comments(file_path)
    else:
        # No specific parser for this extension
        return {}
