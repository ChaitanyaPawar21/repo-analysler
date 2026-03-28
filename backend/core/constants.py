"""
core/constants.py - Application-Wide Constants
===============================================
Centralized constants used across the application.
Avoids magic strings/numbers scattered in service code.
"""

from enum import Enum


# =============================================================================
# Analysis Status
# =============================================================================

class AnalysisStatus(str, Enum):
    """Status of a repository analysis job."""
    PENDING = "pending"
    CLONING = "cloning"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Supported Languages
# =============================================================================

SUPPORTED_LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".php": "php",
}

# =============================================================================
# File Patterns
# =============================================================================

# Files that typically indicate entry points
ENTRY_POINT_PATTERNS = [
    "main.py", "app.py", "index.js", "index.ts", "server.py",
    "manage.py", "wsgi.py", "asgi.py", "main.go", "Main.java",
    "Program.cs", "index.php",
]

# Files/directories to ignore during analysis
IGNORE_PATTERNS = [
    "__pycache__", "node_modules", ".git", ".venv", "venv",
    "dist", "build", ".next", ".cache", "*.pyc", "*.pyo",
    ".env", ".DS_Store", "*.lock",
]

# =============================================================================
# Graph Constants
# =============================================================================

# Maximum depth for dependency graph traversal
MAX_GRAPH_DEPTH = 10

# Node types in the dependency graph
class NodeType(str, Enum):
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    PACKAGE = "package"

# Edge types representing relationships
class EdgeType(str, Enum):
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    DEPENDS_ON = "depends_on"

# =============================================================================
# Embedding Constants
# =============================================================================

# Maximum tokens per chunk for embedding
MAX_CHUNK_TOKENS = 512

# Overlap tokens between consecutive chunks
CHUNK_OVERLAP_TOKENS = 64

# Top-K results for vector similarity search
DEFAULT_TOP_K = 10
