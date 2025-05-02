import os
from asyncio import CancelledError
from typing import AsyncGenerator, Callable, Dict, List, Optional, Tuple

import httpx

from omegacloud_cli import __version__
from omegacloud_cli.common.enums import JobTypeEnum
from omegacloud_cli.common.schemas import (
    AgentInitRequestModel,
    AgentStatusResponseModel,
    ComputeOption,
    TaskInitRequestModel,
    TaskStatusResponseModel,
)
from omegacloud_cli.controllers.filesync import (
    FilesSnapshotModel,
    FilesSyncModel,
    FileSyncManager,
)
from omegacloud_cli.utils.config import load_config

PLATFORM_URL = load_config("platform_url").rstrip("/")


def get_headers() -> Dict[str, str]:
    """Get request headers with auth token."""
    headers = {}
    if token := load_config("apikey"):
        headers["Authorization"] = f"Bearer {token}"
    headers["X-OmegaCloud-CLI-Version"] = __version__
    return headers


# AGENTS


async def init_agent_api(
    size: str,
    disk_size: int,
    storage: List[str],
    environment: Dict[str, str],
    services: Dict[str, Dict[str, str]],
    job_type: JobTypeEnum,
    setup_cmd: List[str],
    run_cmd: List[str],
    build_cmd: List[str],
    fixed_name: Optional[str] = None,
) -> AgentStatusResponseModel:
    url = f"{PLATFORM_URL}/agent/init"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            url,
            json=AgentInitRequestModel(
                size=size,
                disk_size=disk_size,
                storage=storage,
                environment=environment,
                services=services,
                job_type=job_type,
                setup_cmd=setup_cmd,
                run_cmd=run_cmd,
                build_cmd=build_cmd,
                fixed_name=fixed_name,
            ).model_dump(mode="json"),
            headers=get_headers(),
        )
        response.raise_for_status()
        info = AgentStatusResponseModel.model_validate(response.json())
        return info


async def kill_agent_api(agent_id: str) -> AgentStatusResponseModel:
    """Stop a running agent."""
    url = f"{PLATFORM_URL}/agent/{agent_id}/kill"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, headers=get_headers())
        response.raise_for_status()
        return AgentStatusResponseModel.model_validate(response.json())


async def inspect_agent_api(
    agent_id: str,
    process_queue: Optional[str] = None,
    log_start: Optional[int] = -1,
) -> AgentStatusResponseModel:
    """Get status of a agent."""
    url = f"{PLATFORM_URL}/agent/{agent_id}/inspect"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            url,
            headers=get_headers(),
            params={"process_queue": process_queue, "log_start": log_start},
        )
        response.raise_for_status()
        info = AgentStatusResponseModel.model_validate(response.json())
        return info


async def watch_api(
    watch_type: str,
    watch_id: str,
    process_queue: Optional[str] = None,
    log_start: Optional[int] = 0,
) -> AsyncGenerator[str, None]:
    """Stream job output from the API.

    Returns:
        Generator yielding output lines from the job.
        Yields None when job is not ready (HTTP 400).
    """
    url = f"{PLATFORM_URL}/{watch_type}/{watch_id}/watch"
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                url,
                headers=get_headers(),
                params={"process_queue": process_queue, "log_start": log_start},
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    yield chunk
    except CancelledError:
        return
    except Exception:
        return


async def run_agent_api(agent_id: str) -> AgentStatusResponseModel:
    url = f"{PLATFORM_URL}/agent/{agent_id}/run"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, headers=get_headers())
        response.raise_for_status()
        info = AgentStatusResponseModel.model_validate(response.json())
        return info


async def stop_agent_api(agent_id: str) -> bool:
    """Stop a running job."""
    url = f"{PLATFORM_URL}/agent/{agent_id}/stop"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, headers=get_headers())
        response.raise_for_status()
        return response.is_success


async def get_fixed_name_api() -> str:
    url = f"{PLATFORM_URL}/agent/new_name"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, headers=get_headers())
        response.raise_for_status()
        if response.is_success:
            return response.json().get("name")
    return None


async def check_fixed_name_api(
    name: str,
    agent_id: Optional[str] = None,
) -> bool:
    url = f"{PLATFORM_URL}/agent/validate_name"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            url,
            params={"name": name, "agent_id": agent_id},
            headers=get_headers(),
        )
        response.raise_for_status()
        if response.is_success:
            return response.json().get("is_valid")
    return False


# TASKS


async def init_task_api(
    size: str,
    disk_size: int,
    storage: List[str],
    environment: Dict[str, str],
    services: Dict[str, Dict[str, str]],
    schedule: str,
    setup_cmd: List[str],
    run_cmd: List[str],
    build_cmd: List[str],
    fixed_agent_id: Optional[str] = None,
) -> TaskStatusResponseModel:
    url = f"{PLATFORM_URL}/task/init"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            url,
            json=TaskInitRequestModel(
                size=size,
                disk_size=disk_size,
                storage=storage,
                environment=environment,
                services=services,
                setup_cmd=setup_cmd,
                run_cmd=run_cmd,
                build_cmd=build_cmd,
                schedule=schedule,
                fixed_agent_id=fixed_agent_id,
            ).model_dump(mode="json"),
            headers=get_headers(),
        )
        response.raise_for_status()
        info = TaskStatusResponseModel.model_validate(response.json())
        return info


async def enable_task_api(
    task_id: str,
    schedule: str,
    setup_cmd: List[str],
    run_cmd: List[str],
    build_cmd: List[str],
    fixed_agent_id: Optional[str] = None,
) -> TaskStatusResponseModel:
    url = f"{PLATFORM_URL}/task/{task_id}/enable"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            url,
            headers=get_headers(),
            json=TaskInitRequestModel(
                schedule=schedule,
                setup_cmd=setup_cmd,
                run_cmd=run_cmd,
                build_cmd=build_cmd,
                fixed_agent_id=fixed_agent_id,
            ).model_dump(mode="json"),
        )
        response.raise_for_status()
        info = TaskStatusResponseModel.model_validate(response.json())
        return info


async def disable_task_api(
    task_id: str, stop_job: bool = False, stop_agent: bool = False
) -> TaskStatusResponseModel:
    """Disable a task."""
    url = f"{PLATFORM_URL}/task/{task_id}/disable"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            url,
            params={"stop_job": stop_job, "stop_agent": stop_agent},
            headers=get_headers(),
        )
        response.raise_for_status()
        info = TaskStatusResponseModel.model_validate(response.json())
        return info


async def run_task_api(task_id: str) -> TaskStatusResponseModel:
    url = f"{PLATFORM_URL}/task/{task_id}/run"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, headers=get_headers())
        response.raise_for_status()
        info = TaskStatusResponseModel.model_validate(response.json())
        return info


async def stop_task_api(task_id: str) -> bool:
    """Stop a running task."""
    url = f"{PLATFORM_URL}/task/{task_id}/stop"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, headers=get_headers())
        response.raise_for_status()
        return response.is_success


async def inspect_task_api(task_id: str) -> TaskStatusResponseModel:
    """Get status of a task."""
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            f"{PLATFORM_URL}/task/{task_id}/inspect",
            headers=get_headers(),
        )
        response.raise_for_status()
        info = TaskStatusResponseModel.model_validate(response.json())
        return info


# FILES


async def sync_files_api(
    sync_type: str,
    sync_id: str,
    client_snapshot: FilesSnapshotModel,
    storage_name: str = "",
) -> FilesSyncModel:
    """
    Compare client snapshot with server files and return sync actions.

    Args:
        job_id: ID of the job
        client_snapshot: FilesSnapshotModel containing the client file system state

    Returns:
        FilesSyncModel: Contains lists of files to sync in each direction
    """
    url = f"{PLATFORM_URL}/sync/{sync_type}/{sync_id}/sync"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            url,
            json=client_snapshot.model_dump(mode="json"),
            headers=get_headers(),
            params={"storage_name": FileSyncManager.encode_path(storage_name)},
        )
        response.raise_for_status()
        return FilesSyncModel.model_validate(response.json())


async def upload_file_api(
    sync_type: str,
    sync_id: str,
    file_path: str,
    storage_path: str = ".",
    storage_name: str = "",
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> Tuple[bool, Optional[Exception]]:
    """
    Upload a file to the job's shared directory using FileSyncManager.

    Args:
        agent_id: ID of the agent
        file_path: Path to the local file to upload
        progress_callback: Optional callback for progress reporting

    Returns:
        Tuple of (success, error). If error is None, operation was successful.
    """
    try:
        if not os.path.isfile(os.path.join(storage_path, file_path)):
            return False, ValueError(f"File does not exist: {file_path}")
        url = f"{PLATFORM_URL}/sync/{sync_type}/{sync_id}"
        result = await FileSyncManager.upload_file(
            url,
            get_headers(),
            {"storage_name": FileSyncManager.encode_path(storage_name)},
            storage_path,
            file_path,
            progress_callback=progress_callback,
        )
        return result, None
    except Exception as e:
        return False, e


async def download_file_api(
    sync_type: str,
    sync_id: str,
    file_path: str,
    storage_path: str = ".",
    storage_name: str = "",
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> Tuple[bool, Optional[Exception]]:
    """
    Download a file from the job's shared directory using FileSyncManager.

    Args:
        agent_id: ID of the agent
        file_path: Path to the file relative to the job's shared directory
        progress_callback: Optional callback for progress reporting

    Returns:
        Tuple of (success, error). If error is None, operation was successful.
    """
    try:
        url = f"{PLATFORM_URL}/sync/{sync_type}/{sync_id}"
        result = await FileSyncManager.download_file(
            url,
            get_headers(),
            {"storage_name": FileSyncManager.encode_path(storage_name)},
            storage_path,
            file_path,
            progress_callback=progress_callback,
        )
        return result, None
    except Exception as e:
        return False, e


# OTHER


async def get_compute_options_api() -> List[ComputeOption]:
    """Get available compute options from the API.

    Returns:
        List[ComputeOption]: List of compute options available to the user
    """
    url = f"{PLATFORM_URL}/public/compute"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(url)
        response.raise_for_status()
        return [ComputeOption.model_validate(item) for item in response.json()]
