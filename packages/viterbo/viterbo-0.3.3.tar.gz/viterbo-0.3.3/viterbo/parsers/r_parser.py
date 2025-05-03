"""
Parser for R source code.
"""

import re
import sys


def parse_r_file(file_path):
    """
    Parse an R file to extract structure and documentation.

    Args:
        file_path: Path to the R file

    Returns:
        Dictionary with file information
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        result = {
            "type": "r",
            "comments": {},
            "functions": [],
            "imports": [],
            "assignments": [],
        }

        # Extract file-level Roxygen comment
        file_comment_match = re.search(r"^\s*#\'(.*?)(?=\n[^#\'])", content, re.DOTALL)
        if file_comment_match:
            file_comment = file_comment_match.group(1).strip()
            result["comments"]["file"] = re.sub(r"\n\s*#\'\s*", "\n", file_comment)

        # Extract library/package imports
        import_patterns = [
            r'library\s*\(\s*["\']?([^"\'(),\s]+)["\']?\s*\)',
            r'require\s*\(\s*["\']?([^"\'(),\s]+)["\']?\s*\)',
            r'import\s*\(\s*["\']?([^"\'(),\s]+)["\']?\s*\)',
        ]

        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                package_name = match.group(1)
                result["imports"].append(package_name)

        # Extract functions with Roxygen documentation
        function_pattern = (
            r"(#\'.*?)(?=\n[^#\'])\s*([\w_.]+)\s*<-\s*function\s*\((.*?)\)"
        )
        for match in re.finditer(function_pattern, content, re.DOTALL):
            comment = match.group(1).strip()
            comment = re.sub(r"\n\s*#\'\s*", "\n", comment.replace("#'", "", 1))

            function_name = match.group(2).strip()
            parameters = match.group(3).strip()

            # Parse roxygen tags
            tags = {}
            for tag_match in re.finditer(
                r"@(\w+)\s+(.+?)(?=\n\s*@|\n\s*$|\n\s*\n|$)", comment, re.DOTALL
            ):
                tag_name = tag_match.group(1)
                tag_content = tag_match.group(2).strip()
                tags[tag_name] = tag_content

            # Extract function description (text before any @tags)
            description = comment
            first_tag_pos = comment.find("@")
            if first_tag_pos > 0:
                description = comment[:first_tag_pos].strip()

            function_info = {
                "name": function_name,
                "parameters": parameters,
                "description": description,
                "tags": tags,
            }

            result["functions"].append(function_info)
            result["comments"][function_name] = comment

        # Extract assignments (variables, non-function objects)
        assignment_pattern = r"([\w_.]+)\s*<-\s*(?!function\s*\()(.*?)(?=\n|$)"
        for match in re.finditer(assignment_pattern, content):
            variable_name = match.group(1).strip()
            value = match.group(2).strip()

            # Skip if already captured as a function
            if not any(f["name"] == variable_name for f in result["functions"]):
                result["assignments"].append(
                    {
                        "name": variable_name,
                        "value": value[:50] + ("..." if len(value) > 50 else ""),
                    }
                )

        return result

    except Exception as e:
        print(f"Error parsing R file {file_path}: {e}", file=sys.stderr)
        return {"error": str(e)}
