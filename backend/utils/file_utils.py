"""
utils/file_utils.py - File System Utility Functions
=====================================================
Helpers for file operations, content detection, and directory management.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from core.constants import IGNORE_PATTERNS
from core.logger import get_logger

logger = get_logger(__name__)


def get_file_extension(file_path: str) -> str:
    """Return the lowercase file extension (e.g., '.py')."""
    return Path(file_path).suffix.lower()


def is_binary_file(file_path: str, sample_size: int = 8192) -> bool:
    """
    Heuristic check for whether a file is binary.

    Reads the first `sample_size` bytes and checks for null bytes,
    which are a strong indicator of binary content.
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size)
        # Null bytes strongly indicate binary
        if b"\x00" in chunk:
            return True
        # High ratio of non-text bytes suggests binary
        text_chars = bytearray(
            {7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F}
        )
        non_text = sum(1 for byte in chunk if byte not in text_chars)
        return non_text / max(len(chunk), 1) > 0.30
    except (IOError, OSError):
        return True


def read_file_safe(file_path: str, max_size_mb: float = 10.0) -> Optional[str]:
    """
    Safely read a text file with size limits and encoding fallbacks.

    Args:
        file_path: Path to the file.
        max_size_mb: Maximum file size to read (in MB).

    Returns:
        File contents as string, or None if unreadable / too large.
    """
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        return None

    # Check file size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        logger.warning("File too large, skipping", path=file_path, size_mb=round(size_mb, 2))
        return None

    # Skip binary files
    if is_binary_file(file_path):
        return None

    # Try multiple encodings
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, ValueError):
            continue

    logger.warning("Could not decode file", path=file_path)
    return None


def count_lines(file_path: str) -> int:
    """Count the number of lines in a text file."""
    content = read_file_safe(file_path)
    if content is None:
        return 0
    return content.count("\n") + 1


def should_ignore_path(relative_path: str) -> bool:
    """
    Check if a file or directory path should be ignored during analysis.

    Args:
        relative_path: Path relative to the repository root.

    Returns:
        True if the path matches any ignore pattern.
    """
    parts = Path(relative_path).parts
    for part in parts:
        for pattern in IGNORE_PATTERNS:
            if pattern.startswith("*"):
                if part.endswith(pattern[1:]):
                    return True
            elif part == pattern:
                return True
    return False


def cleanup_directory(dir_path: str) -> bool:
    """
    Safely remove a directory and all its contents.

    Args:
        dir_path: Absolute path to the directory.

    Returns:
        True if cleanup was successful.
    """
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            logger.info("Directory cleaned up", path=dir_path)
            return True
        return False
    except Exception as e:
        logger.error("Failed to cleanup directory", path=dir_path, error=str(e))
        return False


def get_directory_stats(dir_path: str) -> dict:
    """
    Compute basic statistics for a directory.

    Returns:
        Dict with total_files, total_dirs, total_size_bytes.
    """
    total_files = 0
    total_dirs = 0
    total_size = 0

    for root, dirs, files in os.walk(dir_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore_path(d)]
        total_dirs += len(dirs)
        for f in files:
            if not should_ignore_path(f):
                total_files += 1
                total_size += os.path.getsize(os.path.join(root, f))

    return {
        "total_files": total_files,
        "total_dirs": total_dirs,
        "total_size_bytes": total_size,
    }
