import asyncio
import hashlib
import os
import stat
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator, Callable, Dict, List, Optional

import aiofiles
import httpx
from pydantic import BaseModel

# Define excluded directories and file patterns
IGNORE_PATTERNS = [
    # IDE
    ".omega",
    ".vscode",
    ".idea",
    ".DS_Store",
    # Environment
    ".git",
    ".env",
    ".local",
    # Python
    "venv",
    ".venv",
    "__pycache__",
    ".jupyter",
    ".ipython",
    ".ipynb_checkpoints",
    # Node
    ".npm",
    "node_modules",
]

# Define patterns that should be synced (build results for Node apps)
ALLOW_PATTERNS = [
    "dist",
    "build",
    "out",
    "public",
    ".next",
    ".nuxt",
    ".svelte-kit",
]

# Constants for file operations
CHUNK_SIZE = 8192  # Default chunk size (8KB)
LARGE_FILE_THRESHOLD = 100 * 1024 * 1024  # 100MB


class FileMetadataModel(BaseModel):
    """Model for file metadata in snapshot."""

    path: str
    size: int
    hash: str
    modified: str  # ISO formatted timestamp


class FilesSnapshotModel(BaseModel):
    """Model for file system snapshot."""

    files: List[FileMetadataModel]


class FilesSyncModel(BaseModel):
    """Model for complete sync response."""

    to_client: List[FileMetadataModel]
    to_server: List[FileMetadataModel]


class FileSyncManager:
    """
    Utility class for file synchronization operations.
    Can be used on both client and server sides.
    """

    @staticmethod
    async def get_ignorepatterns(directory: str) -> List[str]:
        ignore_patterns = []

        # Read .omegaignore file if it exists
        if os.path.exists(omegaignore_path := os.path.join(directory, ".omega", ".omegaignore")):
            with open(omegaignore_path, "r") as f:
                ignore_patterns = split_text(f.read())

        # Read .gitignore file if it exists
        elif os.path.exists(gitignore_path := os.path.join(directory, ".gitignore")):
            with open(gitignore_path, "r") as f:
                ignore_patterns = split_text(f.read())

        # Read .gitignore_Python or .gitignore_Node
        else:
            if os.path.exists(os.path.join(directory, ".omega")):
                languages = ["Python", "Node"]
                # writing standard .gitignore for Python or Node
                for language in languages:
                    language_ignore_path = os.path.join(
                        directory, ".omega", f".gitignore_{language}"
                    )
                    if not os.path.exists(language_ignore_path):
                        # Load standard .gitignore for Python or Node
                        std_gitignore_text = await get_standard_gitignore(language)
                        if std_gitignore_text:
                            with open(language_ignore_path, "w") as f:
                                f.write(std_gitignore_text)

                # reading standard .gitignore for Python or Node
                for language in languages:
                    language_ignore_path = os.path.join(
                        directory, ".omega", f".gitignore_{language}"
                    )
                    if os.path.exists(language_ignore_path):
                        with open(language_ignore_path, "r") as f:
                            std_ignore_patterns = split_text(f.read())
                            ignore_patterns.extend(std_ignore_patterns)

        # add default ignore patterns
        ignore_patterns.extend(IGNORE_PATTERNS)

        # exclude some important patterns (we need build results for Node)
        ignore_patterns = [
            p
            for p in ignore_patterns
            if p not in ALLOW_PATTERNS and p.strip("/") not in ALLOW_PATTERNS
        ]

        return ignore_patterns

    @staticmethod
    async def create_snapshot(directory: str) -> FilesSnapshotModel:
        """Create a snapshot of all files in the directory, respecting .gitignore rules."""
        ignore_patterns = await FileSyncManager.get_ignorepatterns(directory)

        snapshot_tasks = []

        # Walk through directory
        for root, dirs, filenames in os.walk(directory, topdown=True):
            # Filter out ignored directories early - modifying dirs in place affects traversal
            dirs[:] = [
                d
                for d in dirs
                if not any(matches_gitignore_pattern(d, pattern) for pattern in ignore_patterns)
            ]
            for filename in filenames:
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, directory)

                # Skip if file matches any gitignore pattern
                if any(matches_gitignore_pattern(rel_path, pattern) for pattern in ignore_patterns):
                    continue

                # Create task for processing file
                snapshot_tasks.append(FileSyncManager.get_file_metadata(directory, rel_path))

        # Process all files concurrently
        files_snapshot = await asyncio.gather(*snapshot_tasks)

        return FilesSnapshotModel(files=files_snapshot)

    @staticmethod
    async def get_file_metadata(directory: str, rel_path: str) -> FileMetadataModel:
        # Get absolute path
        abs_path = os.path.join(directory, rel_path)

        # Get file stats
        stats = os.stat(abs_path)
        size = stats.st_size
        modified = datetime.fromtimestamp(stats.st_mtime, tz=timezone.utc).isoformat()

        # Calculate file hash
        file_hash = await FileSyncManager.calculate_file_hash(abs_path)

        return FileMetadataModel(path=rel_path, size=size, hash=file_hash, modified=modified)

    @staticmethod
    def compare_snapshots(
        client_snapshot: FilesSnapshotModel, server_snapshot: FilesSnapshotModel
    ) -> FilesSyncModel:
        """
        Compare two snapshots and determine required actions.
        Returns a SyncResponseModel with lists of files to transfer in each direction.
        """
        to_client = []
        to_server = []

        # Create lookup dictionaries for faster comparisons
        client_files_dict = {file.path: file for file in client_snapshot.files}
        server_files_dict = {file.path: file for file in server_snapshot.files}

        # Check for files on server that need to be transferred to client
        for server_file in server_snapshot.files:
            path = server_file.path

            if path not in client_files_dict:
                # File exists on server but not on client
                to_client.append(server_file)
            elif client_files_dict[path].hash != server_file.hash:
                # File exists on both but has different content
                client_time = datetime.fromisoformat(client_files_dict[path].modified)
                server_time = datetime.fromisoformat(server_file.modified)

                # Determine which version is newer
                if server_time > client_time:
                    to_client.append(server_file)
                else:
                    to_server.append(client_files_dict[path])

        # Check for files on client that don't exist on server
        for client_file in client_snapshot.files:
            path = client_file.path
            if path not in server_files_dict:
                # File exists on client but not on server
                to_server.append(client_file)

        return FilesSyncModel(to_client=to_client, to_server=to_server)

    @staticmethod
    async def calculate_file_hash(file_path: str) -> str:
        """Calculate hash for a file, optimized for large files."""
        hasher = hashlib.md5()
        size = os.path.getsize(file_path)

        # For very large files, hash just portions to improve performance
        if size > LARGE_FILE_THRESHOLD:
            async with aiofiles.open(file_path, "rb") as f:
                # Hash first 10MB
                chunk = await f.read(10 * 1024 * 1024)
                hasher.update(chunk)

                # Seek to last 10MB
                await f.seek(-10 * 1024 * 1024, os.SEEK_END)

                # Hash last 10MB
                chunk = await f.read()
                hasher.update(chunk)

                # Include file size in hash to differentiate similarly structured files
                hasher.update(str(size).encode())
        else:
            # Hash entire file for smaller files
            async with aiofiles.open(file_path, "rb") as f:
                chunk_size = 4 * 1024 * 1024  # 4MB chunks
                while True:
                    chunk = await f.read(chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)

        return hasher.hexdigest()

    @staticmethod
    async def stream_file_up(
        filesync_endpoint: str,
        headers: Dict[str, str],
        params: Dict[str, str],
        file_path: str,
        content: AsyncGenerator[bytes, None],
        progress_callback: Optional[Callable[[int], None]] = None,
    ):
        """Stream a file to the remote server with progress reporting."""

        # Create a content generator that calls the progress callback on each chunk
        async def content_with_progress():
            bytes_sent = 0
            async for chunk in content:
                bytes_sent += len(chunk)
                if progress_callback:
                    progress_callback(bytes_sent)
                yield chunk

        async with httpx.AsyncClient(timeout=None) as client:
            # Upload file chunks
            url = f"{filesync_endpoint}/upload"
            params["file_path"] = FileSyncManager.encode_path(file_path)
            request_headers = {"Content-Type": "application/octet-stream"}
            request_headers.update(headers)

            response = await client.post(
                url,
                content=content_with_progress(),
                headers=request_headers,
                params=params,
            )
            response.raise_for_status()

        return True

    @staticmethod
    async def file_reader(
        file_path: str, chunk_size: int = CHUNK_SIZE, total_size: Optional[int] = None
    ) -> AsyncGenerator[bytes, None]:
        """
        Asynchronously read a file in chunks.

        Args:
            file_path: Path to the local file
            chunk_size: Size of chunks to read (in bytes)
            total_size: Optional total size for progress calculation

        Yields:
            Chunks of file data
        """
        async with aiofiles.open(file_path, "rb") as file_handle:
            while True:
                chunk = await file_handle.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @staticmethod
    async def file_writer(
        file_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ):
        """
        Asynchronously write file chunks to disk with progress reporting using a receiving-generator pattern.

        This is a coroutine-based generator that receives chunks through yield and writes them to a file.
        The caller drives the process by sending chunks to this generator.

        Args:
            file_path: Path where to write the file
            progress_callback: Optional callback for progress reporting

        Yields:
            None initially, then expects to receive chunks of bytes that will be written to the file

        Returns:
            True on successful completion
        """
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        bytes_received = 0
        async with aiofiles.open(file_path, "wb") as file_handle:
            # Process chunks as they are sent to the generator
            while True:
                # Yield to receive the next chunk
                chunk = yield
                if chunk is None:
                    break
                await file_handle.write(chunk)
                bytes_received += len(chunk)
                if progress_callback:
                    progress_callback(bytes_received)

        # Set file permissions to rwxrwxrwx (0o777) - read, write, execute for all users
        os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0o777

    @staticmethod
    async def upload_file(
        filesync_endpoint: str,
        headers: Dict[str, str],
        params: Dict[str, str],
        base_path: str,
        file_path: str,
        chunk_size: int = CHUNK_SIZE,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> bool:
        """
        Upload a file to the remote server with progress reporting.

        Args:
            filesync_endpoint: Base URL for the filesync API
            base_path: Base directory for local files
            file_path: Path to the file to upload (relative to base_path)
            chunk_size: Size of chunks to upload
            progress_callback: Optional callback for progress reporting (bytes_sent, total_size)

        Returns:
            True on successful completion
        """
        local_file_path = os.path.join(base_path, file_path)

        content = FileSyncManager.file_reader(local_file_path, chunk_size)
        result = await FileSyncManager.stream_file_up(
            filesync_endpoint,
            headers,
            params,
            file_path,
            content,
            progress_callback,
        )
        return result

    @staticmethod
    async def stream_file_down(
        filesync_endpoint: str,
        headers: Dict[str, str],
        params: Dict[str, str],
        file_path: str,
        chunk_size: int = CHUNK_SIZE,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream a file from the remote server with progress reporting.

        Args:
            filesync_endpoint: Base URL for the filesync API
            file_path: Path to the file on the remote server
            chunk_size: Size of chunks to download
            progress_callback: Optional callback for progress reporting

        Yields:
            Chunks of file data
        """
        async with httpx.AsyncClient() as client:
            url = f"{filesync_endpoint}/download"
            params["file_path"] = FileSyncManager.encode_path(file_path)
            async with client.stream("POST", url, headers=headers, params=params) as response:
                response.raise_for_status()
                bytes_received = 0
                async for chunk in response.aiter_bytes(chunk_size):
                    bytes_received += len(chunk)
                    if progress_callback:
                        progress_callback(bytes_received)
                    yield chunk

    @staticmethod
    async def download_file(
        filesync_endpoint: str,
        headers: Dict[str, str],
        params: Dict[str, str],
        base_path: str,
        file_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> bool:
        """
        Download a file from the remote server in chunks with progress reporting.

        Args:
            filesync_endpoint: Base URL for the filesync API
            base_path: Base directory for local files
            file_path: Path to download (relative to base_path)
            progress_callback: Optional callback for progress reporting (bytes_received, total_size)

        Returns:
            True on successful completion
        """
        local_file_path = os.path.join(base_path, file_path)

        # Get the content stream from the server
        content_stream = FileSyncManager.stream_file_down(
            filesync_endpoint,
            headers,
            params,
            file_path,
            progress_callback=progress_callback,
        )

        # Initialize the file writer generator
        writer = FileSyncManager.file_writer(local_file_path, progress_callback)
        await writer.__anext__()  # Start the writer generator

        # Send each chunk to the writer
        try:
            async for chunk in content_stream:
                await writer.asend(chunk)
            await writer.asend(None)  # Stop the writer generator
        except StopAsyncIteration:
            pass

        return True

    @staticmethod
    async def synchronize_files(
        filesync_endpoint: str,
        headers: Dict[str, str],
        params: Dict[str, str],
        local_snapshot: FilesSnapshotModel,
        remote_snapshot: FilesSnapshotModel,
        base_path: str,
        upload: bool = True,
        download: bool = True,
    ) -> FilesSyncModel:
        """
        Synchronize files between local and remote systems based on snapshot comparison.

        This method:
        1. Compares local and remote snapshots to identify differences
        2. Downloads files that need to be transferred from remote to local
        3. Uploads files that need to be transferred from local to remote

        Args:
            filesync_endpoint: Base URL for the filesync API
            local_snapshot: Snapshot of local files
            remote_snapshot: Snapshot of remote files
            base_path: Base directory for local files
            chunk_size: Size of chunks for file transfer
            progress_callback: Optional callback for progress reporting

        Returns:
            None
        """
        # Compare snapshots to determine which files need to be transferred
        sync_model = FileSyncManager.compare_snapshots(local_snapshot, remote_snapshot)

        if download:
            # Create necessary directories for downloads
            for file_meta in sync_model.to_client:
                dir_path = os.path.dirname(os.path.join(base_path, file_meta.path))
                os.makedirs(dir_path, exist_ok=True)

            # Download files from remote to local
            for file_meta in sync_model.to_client:
                # Download the file
                await FileSyncManager.download_file(
                    filesync_endpoint,
                    headers,
                    params,
                    base_path,
                    file_meta.path,
                )

        if upload:
            # Upload files from local to remote
            for file_meta in sync_model.to_server:
                # Upload the file
                await FileSyncManager.upload_file(
                    filesync_endpoint,
                    headers,
                    params,
                    base_path,
                    file_meta.path,
                )

        # Return the sync model for reference
        return sync_model

    @staticmethod
    async def stream_with_cache(
        stream: AsyncGenerator[bytes, None],
        cache_file_path: str,
    ) -> AsyncGenerator[bytes, None]:
        try:
            cache_writer = FileSyncManager.file_writer(cache_file_path)
            await cache_writer.__anext__()  # Start the writer
            async for chunk in stream:
                await cache_writer.asend(chunk)
                yield chunk
            await cache_writer.asend(None)  # Stop the writer
        except StopAsyncIteration:
            pass

    @staticmethod
    def encode_path(path: str) -> str:
        """
        Encode a file path for safe use in a FastAPI route.
        - Encodes all special characters (including `.` and `/`)
        - Returns a string like: %2Esomefolder%2F%2Esomefile
        """
        return urllib.parse.quote(path, safe="").replace(".", "%2E")


def split_text(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def matches_gitignore_pattern(path: str, pattern: str) -> bool:
    """
    Check if a path matches a gitignore-style pattern.
    Handles directory patterns (ending with '/') and wildcards correctly.
    """
    # Convert path to forward slashes for consistent matching
    path = path.replace(os.sep, "/")

    # Handle directory patterns
    if pattern.endswith("/"):
        pattern = pattern.rstrip("/")
        return path == pattern or path.startswith(pattern + "/")

    # For file patterns, check if the pattern matches any part of the path
    # This matches git's behavior where patterns can match in any subdirectory
    path_parts = path.split("/")
    return any(Path(part).match(pattern) for part in path_parts)


async def get_standard_gitignore(language: str) -> str:
    # language: Python | Node
    std_gitignore_url = (
        f"https://raw.githubusercontent.com/github/gitignore/refs/heads/main/{language}.gitignore"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(std_gitignore_url)
            if response.is_success:
                return response.text
    except Exception:
        pass

    return ""
