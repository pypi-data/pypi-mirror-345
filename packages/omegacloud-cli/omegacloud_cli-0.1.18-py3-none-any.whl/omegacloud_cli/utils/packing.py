import os
import tempfile
import zipfile
from typing import List, Optional


def create_zip_archive(
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    archive_name: Optional[str] = None,
) -> str:
    """Create a zip archive with specified inclusion/exclusion rules.

    Args:
        include_paths: List of paths to include (if None, include everything)
        exclude_paths: List of paths to exclude
        exclude_patterns: List of glob patterns to exclude
        archive_name: Name of the archive (if None, a temporary name is generated)

    Returns:
        Path to the created zip archive
    """
    exclude_paths = exclude_paths or []
    exclude_patterns = exclude_patterns or [".git", ".venv"]

    if archive_name:
        zip_path = os.path.join(tempfile.gettempdir(), archive_name)
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        zip_path = tmp.name
        tmp.close()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Skip excluded directories
            dirs[:] = [
                d
                for d in dirs
                if d not in exclude_patterns and os.path.join(root, d) not in exclude_paths
            ]

            # If include_paths is specified, only process those paths
            if include_paths and not any(
                root.startswith(f".{os.sep}{path}") or root == f".{os.sep}{path}"
                for path in include_paths
            ):
                continue

            # Skip excluded paths
            if any(root.startswith(f".{os.sep}{path}") for path in exclude_paths):
                continue

            for file in files:
                # Skip files matching exclude patterns
                if any(pattern in file for pattern in exclude_patterns):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, ".")
                zipf.write(file_path, arcname)

    return zip_path
