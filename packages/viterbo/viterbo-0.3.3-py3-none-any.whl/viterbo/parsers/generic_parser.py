"""
Generic parser for file types without language-specific parsers.
"""

import re
import sys


def parse_generic_file(file_path):
    """
    Parse a file without language-specific parsing.
    Attempts to extract comments and basic structure.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with basic file information
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        result = {
            "type": "generic",
            "extension": file_path.suffix.lower(),
            "lines": content.count("\n") + 1,
            "size": len(content),
            "comments": [],
            "patterns": {},
        }

        # Detect and count common patterns based on file extension
        ext = file_path.suffix.lower()

        # JavaScript/TypeScript patterns
        if ext in [".js", ".jsx", ".ts", ".tsx"]:
            # Extract JS/TS comments
            block_comments = re.findall(r"/\*\*(.*?)\*/", content, re.DOTALL)
            line_comments = re.findall(r"^\s*//\s*(.+)$", content, re.MULTILINE)

            result["comments"] = [
                c.strip() for c in block_comments + line_comments if c.strip()
            ]

            # Count functions, imports and classes
            result["patterns"]["functions"] = len(
                re.findall(
                    r"function\s+(\w+)|(\w+)\s*=\s*function|(\w+)\s*:\s*function",
                    content,
                )
            )
            result["patterns"]["arrow_functions"] = len(re.findall(r"=>", content))
            result["patterns"]["imports"] = len(
                re.findall(r"import\s+.*?from", content)
            )
            result["patterns"]["classes"] = len(re.findall(r"class\s+(\w+)", content))

        # HTML patterns
        elif ext in [".html", ".htm", ".xhtml"]:
            # Extract HTML comments
            comments = re.findall(r"<!--(.*?)-->", content, re.DOTALL)
            result["comments"] = [c.strip() for c in comments if c.strip()]

            # Count tags and attributes
            result["patterns"]["tags"] = len(re.findall(r"<[a-zA-Z][^>]*>", content))
            result["patterns"]["divs"] = len(re.findall(r"<div[^>]*>", content))
            result["patterns"]["scripts"] = len(re.findall(r"<script[^>]*>", content))
            result["patterns"]["styles"] = len(re.findall(r"<style[^>]*>", content))

        # CSS patterns
        elif ext in [".css", ".scss", ".sass", ".less"]:
            # Extract CSS comments
            comments = re.findall(r"/\*(.*?)\*/", content, re.DOTALL)
            result["comments"] = [c.strip() for c in comments if c.strip()]

            # Count selectors and properties
            result["patterns"]["selectors"] = len(re.findall(r"[^}]*{", content))
            result["patterns"]["classes"] = len(
                re.findall(r"\.[a-zA-Z][\w-]*", content)
            )
            result["patterns"]["ids"] = len(re.findall(r"#[a-zA-Z][\w-]*", content))

        # Markdown patterns
        elif ext in [".md", ".markdown"]:
            # Count headings, links, and code blocks
            result["patterns"]["headings"] = len(
                re.findall(r"^#{1,6}\s+", content, re.MULTILINE)
            )
            result["patterns"]["links"] = len(re.findall(r"\[.+?\]\(.+?\)", content))
            result["patterns"]["code_blocks"] = len(
                re.findall(r"```.*?```", content, re.DOTALL)
            )

        # SQL patterns
        elif ext in [".sql"]:
            # Extract SQL comments
            line_comments = re.findall(r"^\s*--\s*(.+)$", content, re.MULTILINE)
            block_comments = re.findall(r"/\*(.*?)\*/", content, re.DOTALL)

            result["comments"] = [
                c.strip() for c in line_comments + block_comments if c.strip()
            ]

            # Count SQL statements
            result["patterns"]["selects"] = len(
                re.findall(r"\bSELECT\b", content, re.IGNORECASE)
            )
            result["patterns"]["inserts"] = len(
                re.findall(r"\bINSERT\b", content, re.IGNORECASE)
            )
            result["patterns"]["updates"] = len(
                re.findall(r"\bUPDATE\b", content, re.IGNORECASE)
            )
            result["patterns"]["deletes"] = len(
                re.findall(r"\bDELETE\b", content, re.IGNORECASE)
            )
            result["patterns"]["creates"] = len(
                re.findall(r"\bCREATE\b", content, re.IGNORECASE)
            )

        # YAML/JSON patterns
        elif ext in [".yaml", ".yml", ".json"]:
            if ext == ".json":
                # Count JSON objects and arrays
                result["patterns"]["objects"] = len(re.findall(r"{", content))
                result["patterns"]["arrays"] = len(re.findall(r"\[", content))
            else:
                # Extract YAML comments
                comments = re.findall(r"^\s*#\s*(.+)$", content, re.MULTILINE)
                result["comments"] = [c.strip() for c in comments if c.strip()]

                # Count YAML keys and lists
                result["patterns"]["keys"] = len(
                    re.findall(r"^\s*[\w-]+:", content, re.MULTILINE)
                )
                result["patterns"]["lists"] = len(
                    re.findall(r"^\s*-\s+", content, re.MULTILINE)
                )

        # Shell script patterns
        elif ext in [".sh", ".bash"]:
            # Extract shell comments
            comments = re.findall(r"^\s*#\s*(.+)$", content, re.MULTILINE)
            result["comments"] = [c.strip() for c in comments if c.strip()]

            # Count shell commands and functions
            result["patterns"]["functions"] = len(
                re.findall(r"function\s+(\w+)", content)
            )
            result["patterns"]["if_statements"] = len(re.findall(r"\bif\b", content))
            result["patterns"]["loops"] = len(re.findall(r"\bfor\b|\bwhile\b", content))

        # For all other file types
        else:
            # Try some generic patterns to detect comments
            potential_comments = []

            # Try line comments with different markers
            for marker in ["#", "//", "--"]:
                comments = re.findall(
                    rf"^\s*{re.escape(marker)}\s*(.+)$", content, re.MULTILINE
                )
                if comments:
                    potential_comments.extend(
                        [c.strip() for c in comments if c.strip()]
                    )

            # Try block comments
            block_comments = re.findall(r"/\*(.*?)\*/", content, re.DOTALL)
            if block_comments:
                potential_comments.extend(
                    [c.strip() for c in block_comments if c.strip()]
                )

            result["comments"] = potential_comments

        return result

    except Exception as e:
        print(f"Error parsing file {file_path}: {e}", file=sys.stderr)
        return {"error": str(e)}
