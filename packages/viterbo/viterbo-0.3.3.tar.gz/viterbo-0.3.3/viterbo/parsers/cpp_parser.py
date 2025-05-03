"""
Parser for C/C++ source code.
"""

import re
import sys


def parse_cpp_file(file_path):
    """
    Parse a C/C++ file to extract structure and documentation.

    Args:
        file_path: Path to the C/C++ file

    Returns:
        Dictionary with file information
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        result = {
            "type": "cpp",
            "comments": {},
            "includes": [],
            "defines": [],
            "namespaces": [],
            "classes": [],
            "functions": [],
            "structs": [],
            "enums": [],
        }

        # Extract includes
        include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
        includes = re.findall(include_pattern, content)
        result["includes"] = includes

        # Extract defines
        define_pattern = r"#define\s+(\w+)(?:\s+(.+?))?(?:\n|//|/\*)"
        for match in re.finditer(define_pattern, content):
            name = match.group(1)
            value = match.group(2).strip() if match.group(2) else ""
            result["defines"].append({"name": name, "value": value})

        # Extract file-level documentation comment
        file_comment_match = re.search(r"^\s*/\*\*(.*?)\*/\s*", content, re.DOTALL)
        if file_comment_match:
            file_comment = file_comment_match.group(1).strip()
            result["comments"]["file"] = re.sub(r"\n\s*\*\s*", "\n", file_comment)

        # Extract namespaces
        namespace_pattern = r"namespace\s+(\w+)\s*{"
        result["namespaces"] = re.findall(namespace_pattern, content)

        # Extract classes with documentation comments
        class_pattern = r"/\*\*(.*?)\*/\s*(?:template\s*<.*>)?\s*class\s+(\w+)\s*(?::\s*(?:public|private|protected)\s+(\w+))?"
        for match in re.finditer(class_pattern, content, re.DOTALL):
            comment = match.group(1).strip()
            comment = re.sub(r"\n\s*\*\s*", "\n", comment)

            class_name = match.group(2)
            base_class = match.group(3) if match.group(3) else ""

            result["classes"].append(
                {"name": class_name, "base": base_class, "comment": comment}
            )

            result["comments"][class_name] = comment

        # Extract structs with documentation comments
        struct_pattern = r"/\*\*(.*?)\*/\s*struct\s+(\w+)\s*{"
        for match in re.finditer(struct_pattern, content, re.DOTALL):
            comment = match.group(1).strip()
            comment = re.sub(r"\n\s*\*\s*", "\n", comment)

            struct_name = match.group(2)

            result["structs"].append({"name": struct_name, "comment": comment})

            result["comments"][struct_name] = comment

        # Extract functions with documentation comments
        function_pattern = r"/\*\*(.*?)\*/\s*(?:template\s*<.*>)?\s*(?:static\s+|inline\s+|virtual\s+|explicit\s+|constexpr\s+|auto\s+)?(\w+(?:::\w+)*)\s+(\w+)\s*\((.*?)\)"
        for match in re.finditer(function_pattern, content, re.DOTALL):
            comment = match.group(1).strip()
            comment = re.sub(r"\n\s*\*\s*", "\n", comment)

            return_type = match.group(2)
            function_name = match.group(3)
            parameters = match.group(4).strip()

            result["functions"].append(
                {
                    "name": function_name,
                    "return_type": return_type,
                    "parameters": parameters,
                    "comment": comment,
                }
            )

            result["comments"][function_name] = comment

        # Extract enums with documentation comments
        enum_pattern = r"/\*\*(.*?)\*/\s*enum(?:\s+class)?\s+(\w+)\s*{"
        for match in re.finditer(enum_pattern, content, re.DOTALL):
            comment = match.group(1).strip()
            comment = re.sub(r"\n\s*\*\s*", "\n", comment)

            enum_name = match.group(2)

            result["enums"].append({"name": enum_name, "comment": comment})

            result["comments"][enum_name] = comment

        return result

    except Exception as e:
        print(f"Error parsing C/C++ file {file_path}: {e}", file=sys.stderr)
        return {"error": str(e)}
