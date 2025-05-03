"""
Parser for Python source code.
"""

import ast
import sys


def parse_python_file(file_path):
    """
    Parse a Python file to extract structure and documentation.

    Args:
        file_path: Path to the Python file

    Returns:
        Dictionary with file information
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            source = file.read()

        parsed = ast.parse(source)

        result = {
            "type": "python",
            "docstrings": {},
            "functions": [],
            "classes": [],
            "imports": [],
            "assignments": [],
        }

        # Extract module docstring
        if (
            len(parsed.body) > 0
            and isinstance(parsed.body[0], ast.Expr)
            and isinstance(parsed.body[0].value, ast.Constant)
            and isinstance(parsed.body[0].value.value, str)
        ):
            result["docstrings"]["module"] = parsed.body[0].value.value.strip()
        # Handle older Python versions
        elif (
            len(parsed.body) > 0
            and isinstance(parsed.body[0], ast.Expr)
            and isinstance(parsed.body[0].value, ast.Str)
        ):
            result["docstrings"]["module"] = parsed.body[0].value.s.strip()

        # Extract top-level elements
        for node in parsed.body:
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                # Extract imports
                if isinstance(node, ast.Import):
                    for name in node.names:
                        result["imports"].append(
                            {"name": name.name, "alias": name.asname}
                        )
                else:  # ImportFrom
                    module = node.module if node.module else ""
                    for name in node.names:
                        result["imports"].append(
                            {
                                "name": (
                                    f"{module}.{name.name}" if module else name.name
                                ),
                                "alias": name.asname,
                            }
                        )

            elif isinstance(node, ast.FunctionDef) or isinstance(
                node, ast.AsyncFunctionDef
            ):
                # Extract function information
                func_info = {
                    "name": node.name,
                    "async": isinstance(node, ast.AsyncFunctionDef),
                    "args": _extract_function_args(node),
                    "decorators": [_get_decorator_name(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                }
                result["functions"].append(func_info)
                if func_info["docstring"]:
                    result["docstrings"][node.name] = func_info["docstring"].strip()

            elif isinstance(node, ast.ClassDef):
                # Extract class information
                class_info = {
                    "name": node.name,
                    "bases": [_get_base_name(base) for base in node.bases],
                    "methods": [],
                    "decorators": [_get_decorator_name(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                }

                # Extract methods
                for child in node.body:
                    if isinstance(child, ast.FunctionDef) or isinstance(
                        child, ast.AsyncFunctionDef
                    ):
                        method_info = {
                            "name": child.name,
                            "async": isinstance(child, ast.AsyncFunctionDef),
                            "args": _extract_function_args(child),
                            "decorators": [
                                _get_decorator_name(d) for d in child.decorator_list
                            ],
                            "docstring": ast.get_docstring(child),
                        }
                        class_info["methods"].append(method_info)
                        if method_info["docstring"]:
                            result["docstrings"][f"{node.name}.{child.name}"] = (
                                method_info["docstring"].strip()
                            )

                result["classes"].append(class_info)
                if class_info["docstring"]:
                    result["docstrings"][node.name] = class_info["docstring"].strip()

            elif isinstance(node, ast.Assign):
                # Extract top-level assignments
                targets = []
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        targets.append(target.id)
                if targets:
                    result["assignments"].append(
                        {"targets": targets, "value_type": type(node.value).__name__}
                    )

        return result

    except Exception as e:
        print(f"Error parsing Python file {file_path}: {e}", file=sys.stderr)
        return {"error": str(e)}


def _extract_function_args(node):
    """Extract and format function arguments"""
    args = []

    # Add positional arguments
    for arg in node.args.args:
        arg_info = {"name": arg.arg, "type": "positional"}
        if hasattr(arg, "annotation") and arg.annotation:
            if isinstance(arg.annotation, ast.Name):
                arg_info["annotation"] = arg.annotation.id
            elif isinstance(arg.annotation, ast.Attribute):
                arg_info["annotation"] = _get_attribute_name(arg.annotation)
        args.append(arg_info)

    # Add *args
    if node.args.vararg:
        args.append({"name": node.args.vararg.arg, "type": "vararg"})  # *args

    # Add keyword-only arguments
    for arg in node.args.kwonlyargs:
        arg_info = {"name": arg.arg, "type": "keyword_only"}
        if hasattr(arg, "annotation") and arg.annotation:
            if isinstance(arg.annotation, ast.Name):
                arg_info["annotation"] = arg.annotation.id
            elif isinstance(arg.annotation, ast.Attribute):
                arg_info["annotation"] = _get_attribute_name(arg.annotation)
        args.append(arg_info)

    # Add **kwargs
    if node.args.kwarg:
        args.append({"name": node.args.kwarg.arg, "type": "kwarg"})  # **kwargs

    return args


def _get_decorator_name(node):
    """Get the name of a decorator"""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return _get_attribute_name(node.func)
    elif isinstance(node, ast.Attribute):
        return _get_attribute_name(node)
    return "unknown"


def _get_base_name(node):
    """Get the name of a class base"""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return _get_attribute_name(node)
    return "unknown"


def _get_attribute_name(node):
    """Get the full name of an attribute (e.g., module.submodule.name)"""
    if isinstance(node, ast.Attribute):
        return f"{_get_attribute_name(node.value)}.{node.attr}"
    elif isinstance(node, ast.Name):
        return node.id
    return "unknown"
