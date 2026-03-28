"""
services/parser_service.py - Code Parser Service
==================================================
Parses repository files to extract structure, imports, classes, and functions.
Provides the raw data needed by the graph and analysis services.
"""

from pathlib import Path
from typing import List, Dict, Any
import ast

from core.constants import SUPPORTED_LANGUAGES, IGNORE_PATTERNS
from core.logger import get_logger

logger = get_logger(__name__)


class ParserService:
    """
    Parses source code files and extracts structural information.

    Responsibilities:
        - Walk repository directory and identify parseable files.
        - Extract imports, classes, functions, and dependencies per file.
        - Provide structured data for the graph and analysis services.

    Note:
        Currently supports Python via the `ast` module.
        Can be extended with tree-sitter for multi-language support.
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def get_all_files(self) -> List[Dict[str, Any]]:
        """
        Walk the repository and return metadata for all relevant source files.

        Returns:
            List of dicts with keys: path, relative_path, language, size_bytes, line_count.
        """
        files = []
        for file_path in self.repo_path.rglob("*"):
            if not file_path.is_file():
                continue
            if self._should_ignore(file_path):
                continue

            ext = file_path.suffix.lower()
            language = SUPPORTED_LANGUAGES.get(ext)
            if not language:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                line_count = content.count("\n") + 1
            except Exception:
                line_count = 0

            files.append({
                "path": str(file_path),
                "relative_path": str(file_path.relative_to(self.repo_path)),
                "language": language,
                "size_bytes": file_path.stat().st_size,
                "line_count": line_count,
            })

        logger.info("Parsed file listing", total_files=len(files))
        return files

    def parse_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Python file using the AST module to extract structural information.

        Returns:
            Dict with keys: imports, classes, functions, global_vars.
        """
        result = {
            "imports": [],
            "classes": [],
            "functions": [],
            "global_vars": [],
        }

        try:
            source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=file_path)
        except SyntaxError:
            logger.warning("Syntax error while parsing", file=file_path)
            return result

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append({
                        "module": alias.name,
                        "alias": alias.asname,
                        "type": "import",
                    })
            elif isinstance(node, ast.ImportFrom):
                result["imports"].append({
                    "module": node.module or "",
                    "names": [a.name for a in node.names],
                    "type": "from_import",
                    "level": node.level,
                })
            elif isinstance(node, ast.ClassDef):
                result["classes"].append({
                    "name": node.name,
                    "bases": [self._get_name(b) for b in node.bases],
                    "line": node.lineno,
                    "methods": [
                        n.name for n in node.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ],
                })
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Only top-level functions (not methods inside classes)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "args": [a.arg for a in node.args.args],
                    })

        return result

    def _should_ignore(self, file_path: Path) -> bool:
        """Check if a file/directory should be ignored based on IGNORE_PATTERNS."""
        parts = file_path.relative_to(self.repo_path).parts
        for part in parts:
            for pattern in IGNORE_PATTERNS:
                if pattern.startswith("*"):
                    if part.endswith(pattern[1:]):
                        return True
                elif part == pattern:
                    return True
        return False

    @staticmethod
    def _get_name(node) -> str:
        """Extract name from an AST node (for base classes, etc.)."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{ParserService._get_name(node.value)}.{node.attr}"
        return str(node)
