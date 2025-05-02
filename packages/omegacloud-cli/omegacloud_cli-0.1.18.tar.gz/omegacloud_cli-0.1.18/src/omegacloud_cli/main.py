import asyncio
import glob
import json
import os
import re
import time
from asyncio import CancelledError, TimeoutError
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Callable, Dict, List, Optional, Tuple, Union

import asyncclick as click
import httpx
import toml
from cron_descriptor import get_description as get_schedule_description
from croniter import croniter
from InquirerPy import get_style, inquirer
from InquirerPy.base.control import Choice
from packaging import version
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.status import Status

from omegacloud_cli import __version__, api
from omegacloud_cli.common.enums import (
    AgentStatusEnum,
    JobStatusEnum,
    JobTypeEnum,
    TaskStatusEnum,
)
from omegacloud_cli.common.schemas import (
    AgentStatusResponseModel,
    TaskStatusResponseModel,
)
from omegacloud_cli.controllers.filesync import FileSyncManager
from omegacloud_cli.utils.config import (
    load_config,
    load_script,
    save_config,
    save_script,
)
from omegacloud_cli.utils.py_packaging import parse_dependencies
from omegacloud_cli.utils.schedule import cron_to_celery_cron

# Command aliases
ALIASES = {
    "start": "run",
    "logs": "watch",
    "log": "watch",
    "status": "inspect",
    "files": "sync",
}

style = get_style({"question": "bold"}, style_override=False)

console = Console()


def check_for_updates_wrapper(func):
    """Check for updates to the CLI."""

    def display_update_notification(latest_version: str):
        """Display update notification."""
        current_version = __version__
        console.print()
        console.print(
            Panel(
                f"[bold]OmegaCloud CLI update available!   v{current_version} ≫ v{latest_version}[/]\n"
                # f"Changelog: [link=https://github.com/omegacloud/omegacloud-cli/releases]https://github.com/omegacloud/omegacloud-cli/releases[/]\n"
                f"To update, run:   [bold]pip install --upgrade omegacloud-cli[/]",
                title="Update Available",
                border_style="green",
                expand=False,
            )
        )
        console.print()

    @wraps(func)
    async def wrapper(*args, **kwargs):
        """Check for updates to the CLI."""

        fnc_result = await func(*args, **kwargs)

        latest_version = None
        try:
            with httpx.Client() as client:
                response = client.get("https://pypi.org/pypi/omegacloud-cli/json")
                if response.status_code == 200:
                    latest_version = response.json()["info"]["version"]
                    current_version = __version__

                    if version.parse(latest_version) > version.parse(current_version):
                        display_update_notification(latest_version)
        except Exception:
            pass

        return fnc_result

    return wrapper


def try_except_wrapper(func):
    """
    A decorator that wraps functions with common error handling logic.
    Handles KeyboardInterrupt, CancelledError, HTTPStatusError, ConnectError and general exceptions.
    """

    def extract_error_message(e: Exception) -> str:
        if hasattr(e, "response") and hasattr(e.response, "text"):
            error_text = e.response.text
            try:
                error_json = json.loads(error_text)
                return error_json.get("detail", str(e))
            except json.JSONDecodeError:
                return error_text
        else:
            return str(e)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (KeyboardInterrupt, CancelledError):
            console.print("[yellow]Operation cancelled.[/]")
            console.print()
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [401, 403]:
                console.print("[red]Authentication failed. Please login by > omega login.[/]")
            elif e.response.status_code in [500]:
                console.print(f"[red]An error occurred: {extract_error_message(e)}[/]")
            else:
                console.print(f"[red]An error occurred: {extract_error_message(e)}[/]")
            raise click.Abort()
        except httpx.ConnectError as e:
            console.print(
                f"[red]Omega Platform is now unavailable. Please try again later. {extract_error_message(e)}[/]"
            )
            raise click.Abort()
        except Exception as e:
            console.print(f"[red]An error occurred: {extract_error_message(e)}[/]")
            raise click.Abort()

    return wrapper


def check_auth_wrapper(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        """Check if user is authenticated and initiate login flow if not."""
        if not load_config("apikey"):
            console.print("[yellow]Authentication required[/]")
            await login_flow()
        return await func(*args, **kwargs)

    return wrapper


# Custom Click Group to handle aliases
class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        # Resolve alias to the actual command
        cmd_name = ALIASES.get(cmd_name, cmd_name)
        return super().get_command(ctx, cmd_name)


@click.group(cls=AliasedGroup)
# @click.option("--dev", is_flag=True, help="Run in development mode")
# @click.option("--test", is_flag=True, help="Run in test mode")
def cli():
    """
    OmegaCloud: One-click platform for AI-apps deployment

    CLI version: v.0.1.13 / for update: pip install --upgrade omegacloud-cli
    """
    # Store the flags in the context for use in subcommands
    # ctx = click.get_current_context()
    # ctx.ensure_object(dict)
    # ctx.obj["dev_mode"] = dev
    # ctx.obj["test_mode"] = test
    pass


@cli.command(name="login", help="Login to Omega Cloud")
@check_for_updates_wrapper
async def cli_login():
    """Login to Omega Cloud."""
    await login_flow()


@cli.command(name="run", help="Run a new Job | aliases: start")
@check_auth_wrapper
@check_for_updates_wrapper
@try_except_wrapper
async def cli_run():
    """Start a new job"""
    # ctx = click.get_current_context()
    # dev_mode = ctx.obj.get("dev_mode", False)
    # test_mode = ctx.obj.get("test_mode", False)

    # if dev_mode:
    #     console.print("[yellow]Running in development mode[/]")
    # if test_mode:
    #     console.print("[yellow]Running in test mode[/]")

    with console.status("") as status:
        await run_flow(status)


@cli.command(name="stop", help="Stop a running job")
@check_auth_wrapper
@check_for_updates_wrapper
@try_except_wrapper
async def cli_stop():
    """Stop a running job."""
    with console.status("") as status:
        await stop_flow(status)


@cli.command(name="inspect", help="Get status of a job | aliases: status")
@check_auth_wrapper
@check_for_updates_wrapper
@try_except_wrapper
async def cli_inspect():
    """Get status of a job."""
    with console.status("") as status:
        await inspect_flow(status)


@cli.command(name="watch", help="Watch logs from the job | aliases: logs")
@check_auth_wrapper
@check_for_updates_wrapper
@try_except_wrapper
async def cli_watch():
    """Watch logs from the job."""
    with console.status("") as status:
        await watch_flow(status)


@cli.command(name="sync", help="Synchronize files | aliases: files")
@check_auth_wrapper
@check_for_updates_wrapper
@try_except_wrapper
async def cli_sync():
    """Synchronize files with the job."""
    with console.status("[bold cyan]Analyzing files for sync...[/]") as status:
        if load_config("job_schedule"):
            sync_type = "task"
        else:
            sync_type = "agent"
        await sync_flow(status, sync_type=sync_type, operations="upload+download")


@cli.command(name="config", help="Configure Omega Run")
@check_auth_wrapper
@check_for_updates_wrapper
@try_except_wrapper
async def cli_config():
    """Configure CLI parameters."""

    """Check if there are any running processes that would prevent configuration changes."""
    agent_id = get_agent_id(raise_error=False)
    agent_info = await inspect_agent(agent_id)
    if agent_info and agent_info.agent_status in [AgentStatusEnum.BUSY, AgentStatusEnum.IDLE]:
        console.print("[red]Cannot modify configuration while application is running[/]")
        raise click.Abort()

    task_id = get_task_id(raise_error=False)
    task_info = await inspect_task(task_id)
    if task_info and task_info.task_status == TaskStatusEnum.ON:
        console.print("[red]Cannot modify configuration while job is scheduled[/]")
        raise click.Abort()

    with console.status("") as status:
        await config_flow(status, force_config=True)


# FLOWS


async def login_flow():
    """Handle user login flow."""
    console.print()
    console.print("Please visit: [bold]https://omegacloud.ai/user[/]")
    console.print("Get your access token and paste it below")
    console.print()

    token = await inquirer.text(
        message="Enter your access token:",
        style=style,
    ).execute_async()

    save_config({"apikey": token})
    console.print("[green]Token saved successfully[/]")
    console.print("Note: You can update your token anytime by running: [bold]omega login[/]")
    console.print()


async def sync_flow(status: Status, sync_type: str, operations: str = "upload+download") -> bool:
    """
    File Synchronization Procedure
    """

    status.update("[bold cyan]Syncing files...[/]")
    sync_error = False

    if sync_type == "task":
        sync_id = get_task_id()
    else:
        sync_id = get_agent_id()

    sync_dirs = []
    sync_dirs.append({"path": os.getcwd(), "storage_name": ""})
    storage_list = load_config("storage")
    for storage_name in storage_list:
        sync_dirs.append(
            {
                "path": os.path.join(os.getcwd(), ".omega", "storage", storage_name),
                "storage_name": storage_name,
            }
        )

    for sync_dir in sync_dirs:
        storage_path = sync_dir["path"]
        storage_name = sync_dir["storage_name"]

        if storage_name:
            status.update(f"[bold cyan]Syncing storage '{storage_name}'...[/]")

        # Create snapshot for this directory
        snapshot = await FileSyncManager.create_snapshot(storage_path)

        # Get sync actions from the server
        sync_result = await api.sync_files_api(
            sync_type,
            sync_id,
            snapshot,
            storage_name,
        )

        to_client_count = len(sync_result.to_client)
        to_server_count = len(sync_result.to_server)

        # Stop the status completely before starting the progress display
        # to avoid overlap between status and progress
        status.stop()

        if (to_client_count == 0 or "download" not in operations) and (
            to_server_count == 0 or "upload" not in operations
        ):
            if storage_name:
                console.print(f"[green]All files are in sync @ {storage_name}[/]")
            else:
                console.print("[green]All files are in sync[/]")
            console.print()
            status.start()
            continue

        elif (to_client_count == 0 or "download" not in operations) and to_server_count > 0:
            # no need to ask, just upload
            choice = "upload"

        else:
            # Print sync summary
            if storage_name:
                console.print(f"\n[cyan]File-sync status @ {storage_name}[/]")
            else:
                console.print("\n[cyan]File-sync status:[/]")

            if to_client_count > 0:
                console.print(f"Files to download: [bold]{to_client_count}[/]")
                for file in sync_result.to_client[:10]:
                    console.print(f" - {file.path}")
                if to_client_count > 10:
                    console.print(f" - and {to_client_count - 10} more...")
                console.print()

            if to_server_count > 0:
                console.print(f"Files to upload: [bold]{to_server_count}[/]")
                for file in sync_result.to_server[:10]:
                    console.print(f" - {file.path}")
                if to_server_count > 10:
                    console.print(f" - and {to_server_count - 10} more...")
                console.print()

            # Ask for confirmation before proceeding
            if to_client_count * to_server_count > 0:
                choices = [
                    ("sync-all", "Proceed with sync"),
                    ("download", "Download only"),
                    ("upload", "Upload only"),
                    ("cancel", "Do not sync"),
                ]
            else:
                choices = [
                    ("sync-all", "Proceed with sync"),
                    ("cancel", "Do not sync"),
                ]

            choice = await ask(
                status,
                "Do you want to proceed with the sync?",
                choices,
                default="sync-all",
                timeout=30,
            )

        if choice == "cancel":
            console.print("[yellow]Operation cancelled.[/]")
            status.start()
            sync_error = True
            continue

        # Add a blank line to create separation
        console.print()

        batch_size = 15

        # Process downloads first if stopping
        if to_client_count > 0 and choice in ["sync-all", "download"]:
            files_from = 0  # inclusive
            files_to = min(len(sync_result.to_client), batch_size)  # exclusive

            while files_from < files_to:
                console.print(
                    f"[green]Downloading files from server [{files_from + 1}-{files_to} / {len(sync_result.to_client)}]...[/]"
                )

                # Execute sync operations with Progress
                with Progress() as progress:
                    # Create individual tasks for each download
                    download_tasks = {}
                    for file_meta in sync_result.to_client[files_from:files_to]:
                        # Create a task with the file size as the total
                        download_task_id = progress.add_task(
                            f"[green]Downloading {file_meta.path}[/]",
                            total=file_meta.size,
                            completed=0,
                        )
                        download_tasks[file_meta.path] = download_task_id

                    # Process each download
                    for file_meta in sync_result.to_client[files_from:files_to]:
                        download_task_id = download_tasks[file_meta.path]
                        download_callback = make_progress_callback(progress, download_task_id)

                        success, error = await api.download_file_api(
                            sync_type,
                            sync_id,
                            file_meta.path,
                            storage_path,
                            storage_name,
                            download_callback,
                        )

                        if success:
                            progress.update(
                                download_task_id,
                                completed=file_meta.size,
                                description=f"[green]Completed: {file_meta.path}[/]",
                            )
                        elif error:
                            sync_error = True
                            console.print(f"[red]Failed download {file_meta.path}: {str(error)}[/]")
                            progress.update(
                                download_task_id,
                                completed=file_meta.size,
                                description=f"[red]Failed: {file_meta.path}",
                            )
                        else:
                            sync_error = True
                            console.print(f"[red]Failed download {file_meta.path}[/]")
                            progress.update(
                                download_task_id,
                                completed=file_meta.size,
                                description=f"[red]Failed: {file_meta.path}",
                            )
                files_from = files_to
                files_to = min(files_from + batch_size, len(sync_result.to_client))

        # Process uploads first if starting
        if to_server_count > 0 and choice in ["sync-all", "upload"]:
            files_from = 0  # inclusive
            files_to = min(len(sync_result.to_server), batch_size)  # exclusive

            while files_from < files_to:
                console.print(
                    f"[blue]Uploading files to server [{files_from + 1}-{files_to} / {len(sync_result.to_server)}]...[/]"
                )

                # Execute sync operations with Progress
                with Progress() as progress:
                    # Create individual tasks for each upload
                    upload_tasks = {}
                    for file_meta in sync_result.to_server[files_from:files_to]:
                        # Create a task with the file size as the total
                        upload_task_id = progress.add_task(
                            f"[blue]Uploading {file_meta.path}",
                            total=file_meta.size,
                            completed=0,
                        )
                        upload_tasks[file_meta.path] = upload_task_id

                    # Process each upload
                    for file_meta in sync_result.to_server[files_from:files_to]:
                        upload_task_id = upload_tasks[file_meta.path]
                        upload_callback = make_progress_callback(progress, upload_task_id)

                        success, error = await api.upload_file_api(
                            sync_type,
                            sync_id,
                            file_meta.path,
                            storage_path,
                            storage_name,
                            upload_callback,
                        )

                        if success:
                            progress.update(
                                upload_task_id,
                                completed=file_meta.size,
                                description=f"[blue]Completed: {file_meta.path}",
                            )
                        elif error:
                            sync_error = True
                            console.print(f"[red]Failed upload {file_meta.path}: {str(error)}[/]")
                            progress.update(
                                upload_task_id,
                                completed=file_meta.size,
                                description=f"[red]Failed: {file_meta.path}",
                            )
                        else:
                            sync_error = True
                            console.print(f"[red]Failed upload {file_meta.path}[/]")
                            progress.update(
                                upload_task_id,
                                completed=file_meta.size,
                                description=f"[red]Failed: {file_meta.path}",
                            )
                    files_from = files_to
                    files_to = min(files_from + batch_size, len(sync_result.to_server))

    synced = not sync_error

    console.print("[green]Sync completed![/]")
    console.print("Note: You can sync your files anytime by running: [bold]omega sync[/]")
    console.print()
    status.start()
    return synced


async def watch_flow(status: Status):
    status.update("[bold cyan]Watching for the logs... (safe to CTRL+C)[/]")
    console.print()
    watch_id = None
    if agent_id := get_agent_id(raise_error=False):
        watch_type = "agent"
        watch_id = agent_id
        await inspect_agent(watch_id, get_logs=True)

    elif task_id := get_task_id(raise_error=False):
        watch_type = "task"
        watch_id = task_id

    if watch_id:
        queue_name = load_config("job_type", None)
        log_start = get_logs_length(watch_id, queue_name)
        if log_start > 0:
            # load last 10 lines
            show_prev_logs = 10
            log_file_path_rel = os.path.join(".omega", "logs", f"{watch_id}.{queue_name}.log")
            log_file_path = os.path.join(os.getcwd(), log_file_path_rel)
            if log_start > show_prev_logs:
                console.print(f"...[full log available at {log_file_path_rel}]...", markup=False)
                console.print(
                    f"...[{log_start - show_prev_logs} log lines skipped]...", markup=False
                )
            with open(log_file_path, "r") as f:
                lines = f.readlines()
                last_lines = lines[-show_prev_logs:]
                for line in last_lines:
                    console.print(line, highlight=False, markup=False, end="")

        async for chunk in api.watch_api(watch_type, watch_id, queue_name, log_start):
            console.print(chunk, highlight=False, markup=False, end="")
    else:
        console.print("[red]Nothing to watch[/]")


async def inspect_flow(status: Status):
    status.update("[bold cyan]Inspecting your application...[/]")

    # job_type = load_config("job_type")
    job_schedule = load_config("job_schedule")

    if agent_id := get_agent_id(raise_error=False):
        agent_info = await inspect_agent(agent_id)
        info_dict = agent_info.model_dump()

        job_status = agent_info.job_status or JobStatusEnum.STOPPED
        job_status_value = job_status.value.upper()

        if (
            not agent_info
            or not agent_info.agent_status
            or agent_info.agent_status in [AgentStatusEnum.DEAD]
        ):
            console.print("[red]No active server found[/]")
        elif agent_info.agent_status in [AgentStatusEnum.INIT]:
            console.print("[yellow]Server is initializing[/]")
        elif agent_info.agent_status in [AgentStatusEnum.IDLE]:
            console.print("[yellow]Application is not running[/]")
        elif agent_info.agent_status in [AgentStatusEnum.BUSY]:
            console.print("[green]Application is running[/]")
        else:
            console.print(f"[red]Unknown status: {job_status_value}[/]")
            raise click.Abort()

        for key, val in info_dict.items():
            title = key.replace("_", " ").title()
            title = title.replace("Agent", "Server")
            value = val.value.upper() if isinstance(val, Enum) else val
            if "logs" not in key:
                if value:
                    console.print(f"{title}: {value}")
            else:
                print_logs("Application Logs", val)

        console.print()

    if (task_id := get_task_id(raise_error=False)) and job_schedule:
        task_info = await inspect_task(task_id)
        info_dict = task_info.model_dump()

        task_status = task_info.task_status
        if not task_info or not task_info.task_status:
            console.print("[red]No scheduled job found[/]")
        elif task_status == TaskStatusEnum.ON:
            console.print("[green]Scheduled job is enabled[/]")
        elif task_status == TaskStatusEnum.OFF:
            console.print("[yellow]Scheduled job is disabled[/]")
        else:
            console.print(f"[red]Unknown status: {task_status}[/]")
            raise click.Abort()

        for key, val in info_dict.items():
            title = key.replace("_", " ").title()
            value = val.value.upper() if isinstance(val, Enum) else val
            if "schedule" in key:
                console.print(f"{title} (cron): {value}")
                console.print(f"{title}: {get_schedule_description(value)}")
            elif "logs" not in key:
                if value:
                    console.print(f"{title}: {value}")
            elif not agent_id:
                print_logs("Scheduled Job Logs", val)

        console.print()


async def disk_flow():
    # Ask user to input disk size

    # Read previous disk size from config file
    compute_size = load_config("compute_size", None)
    compute_size_type = compute_size.split("-")[0] if compute_size else None

    if compute_size_type == "cpu":
        disk_min = 8
        disk_max = 1000
        disk_size_default = "12"
    else:
        disk_min = 30
        disk_max = 1000
        disk_size_default = "50"

    disk_size = load_config("disk_size", disk_size_default)

    while True:
        disk_size = await inquirer.text(
            message=f"Enter disk size in GB [{disk_min}-{disk_max}]:",
            default=disk_size,
            style=style,
        ).execute_async()

        try:
            disk_size_int = int(disk_size)
            if disk_min <= disk_size_int <= disk_max:
                break
            else:
                console.print(f"[red]Disk size must be between {disk_min} and {disk_max} GB.[/]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/]")

    console.print()

    # Save the selected disk size to config file
    save_config({"disk_size": disk_size})

    return disk_size


async def schedule_flow() -> str:
    schedule_mapping = {
        "once": "",
        "hourly": "0 * * * *",
        "daily": "0 0 * * *",
        "weekly": "0 0 * * 0",
        "monthly": "0 0 1 * *",
    }

    schedule_mapping_reverse = {v: k for k, v in schedule_mapping.items()}
    job_schedule = load_config("job_schedule", "0 0 * * *")
    schedule_choice = schedule_mapping_reverse.get(job_schedule, "$custom")

    choices = [
        Choice(value="once", name="Once"),
        Choice(value="hourly", name="Every hour"),
        Choice(value="daily", name="Every day"),
        Choice(value="weekly", name="Every week"),
        Choice(value="monthly", name="Every month"),
        Choice(value="$custom", name="Custom"),
    ]

    schedule_choice = await inquirer.select(
        message="Select job schedule:",
        choices=choices,
        default=schedule_choice,
        style=style,
    ).execute_async()

    job_schedule_input = schedule_mapping.get(schedule_choice, None)
    if job_schedule_input is not None:
        job_schedule = job_schedule_input
    else:
        console.print("Input cron schedule for your job")
        console.print("For reference, visit: [bold]https://crontab.guru/[/bold]")

        # Loop until valid cron format is entered
        valid_format = False
        while not valid_format:
            job_schedule = await inquirer.text(
                message="Cron schedule:",
                style=style,
                default=job_schedule,
            ).execute_async()
            valid_format = validate_cron_format(job_schedule)
            if not valid_format:
                console.print("[red]Invalid cron format. Please try again.[/red]")
            else:
                console.print(f"Your schedule: {get_schedule_description(job_schedule)}")
                # ask confirmation
                choices = [
                    Choice(value="yes", name="Yes"),
                    Choice(value="no", name="No"),
                ]
                confirmation = await inquirer.select(
                    message="Is this correct?",
                    choices=choices,
                ).execute_async()
                if confirmation == "no":
                    valid_format = False

    console.print()
    save_config({"job_schedule": job_schedule})

    # Load task.sh script for user display
    # script = load_script("task.sh")
    # task_command = "& ".join(script) if script else "python main.py"

    # # Ask user to input task run command
    # task_command = await inquirer.text(
    #     message="Enter command to run your task:",
    #     style=style,
    #     default=task_command,
    # ).execute_async()

    # # Split command by ; and clean up whitespace
    # commands = [cmd.strip() for cmd in task_command.split("&")]
    # save_script("task.sh", commands)

    return job_schedule


async def select_script_commands_flow(
    title: str, available_scripts: Dict[str, str], script_command: str = None
) -> List[str]:
    """Select a script from the available scripts or enter a custom command."""
    script = "$custom"
    if available_scripts:
        # select script
        choices = [Choice(value=k, name=f"{k}: {v}") for k, v in available_scripts.items()]
        if script_command and script_command not in available_scripts.keys():
            choices.append(Choice(value=script_command, name=script_command))

        if script_command and script_command in available_scripts.keys():
            default = script_command
        else:
            default = choices[0].value

        choices.append(Choice(value="$custom", name="Custom"))

        script = await inquirer.select(
            message=f"Select script to {title}:",
            choices=choices,
            default=default,
        ).execute_async()

    if script == "$custom":
        script_command = await inquirer.text(
            message=f"Enter command to {title}:",
            style=style,
            default=script_command,
        ).execute_async()
        script_commands = [cmd.strip() for cmd in script_command.split("&")]
    else:
        script_commands = [script]

    console.print()
    return script_commands


async def commands_flow(job_type: JobTypeEnum):
    """Detect the job type based on the files in the current directory.

    Returns:
        JobTypeEnum: The job type.
    """

    if job_type != JobTypeEnum.LAB:
        console.print(Panel("[bold]Run commands[/]", expand=False))

    # Load existing commands
    setup_commands = load_script("setup.sh")
    build_commands = []
    run_commands = []
    task_commands = []

    framework = await autodetect_framework()

    job_schedule = load_config("job_schedule")

    # Needs for API
    # API not schedule: build, run
    # API + schedule: build, run, task
    # JOB not schedule: build, run
    # JOB + schedule: build, task
    # LAB: nothing

    if job_type in [JobTypeEnum.API, JobTypeEnum.JOB]:
        # Asking for build commands
        build_commands = load_script("build.sh")
        if not build_commands:
            build_commands = autodetect_build_commands()

        if framework == "node":
            console.print()
            console.print(
                "[bold]Important![/] Build your node application locally before running it on Omega Cloud!"
            )

        # Ask user to input BUILD commands (install dependencies)
        build_commands = await select_script_commands_flow(
            "install dependencies",
            None,
            " & ".join(build_commands),
        )

    if (job_type == JobTypeEnum.API) or (job_type == JobTypeEnum.JOB and not job_schedule):
        # Asking for run commands for API/WEB applications or JOB without schedule (one-time job)
        run_commands = load_script("run.sh")
        if not run_commands:
            run_commands = await autodetect_run_commands()

        # Ask user to input app RUN commands
        if job_type in JobTypeEnum.API:
            console.print("[bold]Important![/] Run your API/WEB on [bold]8008[/] port!")

        available_scripts = None
        if framework == "node":
            available_scripts = get_node_scripts()

        run_commands = await select_script_commands_flow(
            "run your application",
            available_scripts,
            " & ".join(run_commands),
        )

    if job_type in [JobTypeEnum.API, JobTypeEnum.JOB] and job_schedule:
        # Asking for task commands for scheduled jobs
        task_commands = load_script("task.sh")
        if not task_commands:
            task_commands = autodetect_task_commands()

        # Ask user to input app TASK commands
        available_scripts = None
        if framework == "node":
            available_scripts = get_node_scripts()

        task_commands = await select_script_commands_flow(
            "run your scheduled task",
            available_scripts,
            " & ".join(task_commands),
        )

    if job_type == JobTypeEnum.LAB:
        # For LAB type, create empty *.sh
        pass

    save_script("run.sh", run_commands)
    save_script("build.sh", build_commands)
    save_script("task.sh", task_commands)
    save_script("setup.sh", setup_commands)


async def type_flow() -> Tuple[JobTypeEnum, str]:
    console.print(Panel("[bold]Application type[/]", expand=False))

    detected_job_type = await autodetect_job_type()
    job_type = load_config("job_type", detected_job_type.value)

    choices = [
        Choice(
            value="api",
            name="API/Web - Start an Web-service (e.g. FastAPI/Flask) or Web-site (e.g. Node/React)",
        ),
        Choice(value="job", name="Job - Run a program (one-time or periodically)"),
        Choice(value="lab", name="Lab - Launch a Lab (Jupyter Notebook)"),
    ]

    job_type = await inquirer.select(
        message="Select your run type:",
        choices=choices,
        default=job_type,
        style=style,
    ).execute_async()
    console.print()

    if job_type == "job":
        job_schedule = await schedule_flow()

    elif job_type == "api":
        # Ask user to get fixed domain name for the API
        fixed_name = load_config("fixed_name", "")
        valid_fixed_name = False
        console.print(
            "Your Web/API will be available at [bold]https://YOURNAME.run.omegacloud.ai[/]"
        )
        while not valid_fixed_name:
            fixed_name = await inquirer.text(
                message="Enter preferred YOURNAME for your Web/API (or press ENTER for random):",
                default=fixed_name,
                style=style,
            ).execute_async()
            valid_fixed_name = await validate_fixed_name(fixed_name)
            if not valid_fixed_name:
                console.print(
                    f"[red]Name {fixed_name} is unavailable or incorrect. Please try again.[/]"
                )
            elif fixed_name:
                console.print(
                    f"Your Web/API will be available at [bold green]https://{fixed_name}.run.omegacloud.ai[/]"
                )
        console.print()
        save_config({"fixed_name": fixed_name})

        # Ask if user wants to add a schedule job for the API
        current_schedule = load_config("job_schedule", None)
        choices = [
            Choice(value="no", name="No, just run API/WEB application"),
            Choice(value="yes", name="Yes, add scheduled job to my API/WEB application"),
        ]
        schedule_task = await inquirer.select(
            message="Would you like to add a scheduled job on top of your API/WEB application?",
            choices=choices,
            default="yes" if current_schedule else "no",
            style=style,
        ).execute_async()
        console.print()

        if schedule_task == "yes":
            job_schedule = await schedule_flow()
        else:
            job_schedule = ""

    elif job_type == "lab":
        job_schedule = ""

    if job_type == "job":
        save_config({"agent_id": None})
    elif not job_schedule:
        save_config({"task_id": None})

    save_config({"job_type": job_type, "job_schedule": job_schedule})
    await commands_flow(JobTypeEnum(job_type))

    return JobTypeEnum(job_type), job_schedule


async def storage_flow():
    """Ask user to type storage names, separated by commas. return list of storage names."""

    console.print(Panel("[bold]Shared storage (optional)[/]", expand=False))

    # Read previous disk size from config file
    storage_list = load_config("storage", [])

    console.print(
        "If you have several applications sharing the same files, you can use shared storage"
    )
    console.print("Shared storage is sync automatically between your jobs")
    console.print("Your app can use shared storage located at: [bold]/tmp/<storage_name>[/]")
    storage_text = await inquirer.text(
        message="Enter shared storage names (or press ENTER to skip):",
        style=style,
        default=", ".join(storage_list),
    ).execute_async()
    console.print()

    storage_list = storage_text.split(",")
    storage_list = [s.strip() for s in storage_list if s.strip()]
    save_config({"storage": storage_list})

    if len(storage_list) > 1:
        console.print(
            "Shared storages are synced automatically between your applications every 5 minutes"
        )
        console.print("Shared storages are available for your application at:")
    elif len(storage_list) > 0:
        console.print(
            "Shared storage is synced automatically between your applications every 5 minutes"
        )
        console.print("Note: Shared storage is available for your application at:")
    for storage in storage_list:
        console.print(f" - /tmp/{storage}")

    console.print()

    return storage_list


async def size_flow(
    job_type: JobTypeEnum, force_config: bool = False, show_panel: bool = True
) -> str:
    if show_panel:
        console.print(Panel("[bold]Compute size[/]", expand=False))

    title = get_job_title(job_type)
    compute_size = load_config("compute_size", None)

    # Get compute options from API
    compute_options = await api.get_compute_options_api()

    # Separate CPU and GPU options
    cpu_options = [opt for opt in compute_options if opt.code.startswith("cpu")]
    gpu_options = [opt for opt in compute_options if opt.code.startswith("gpu")]

    if job_type == JobTypeEnum.LAB:
        compute_type = "gpu"
    else:
        compute_type = "cpu"

    compute_size = (
        f"{compute_type}-m"
        if not compute_size or not compute_size.startswith(compute_type)
        else compute_size
    )

    # if (compute_size is None or force_config) and job_type != JobTypeEnum.LAB:
    # cpu_price_min = min([o.price for o in cpu_options]) * 750  # month
    # cpu_price_max = max([o.price for o in cpu_options]) * 750  # month
    # gpu_price_min = min([o.price for o in gpu_options])  # hour
    # gpu_price_max = max([o.price for o in gpu_options])  # hour

    #     # Create top level choices for CPU vs GPU
    #     cpu_choice = Choice(
    #         value="cpu",
    #         name=f"CPU (${cpu_price_min:.2f} .. ${cpu_price_max:.2f}/month)",
    #     )
    #     gpu_choice = Choice(
    #         value="gpu",
    #         name=f"GPU (${gpu_price_min:.2f} .. ${gpu_price_max:.2f}/hour)",
    #     )

    #     choices = [cpu_choice, gpu_choice]

    #     compute_type = await inquirer.select(
    #         message=f"Select compute for your {title}:",
    #         choices=choices,
    #         default=choices[0].value,
    #         style=style,
    #     ).execute_async()
    #     compute_size = (
    #         f"{compute_type}-m"
    #         if not compute_size or not compute_size.startswith(compute_type)
    #         else compute_size
    #     )

    if job_type == JobTypeEnum.LAB or ("gpu" in compute_size):
        # Calculate max lengths for formatting
        max_title_length = max([len(opt.title) for opt in gpu_options]) + 2
        max_desc_length = max([len(opt.description) for opt in gpu_options]) + 2

        # Create choices for GPU sizes
        choices = [
            Choice(
                value=opt.code,
                name=f"{opt.title:{max_title_length}} : {opt.description:{max_desc_length}} : {opt.price_tag}",
            )
            for opt in gpu_options
        ]

        compute_size = await inquirer.select(
            message=f"Select GPU size for your {title}:",
            choices=choices,
            default=compute_size or choices[0].value,
            style=style,
        ).execute_async()

    else:
        # Calculate max lengths for formatting
        max_title_length = max([len(opt.title) for opt in cpu_options]) + 2
        max_desc_length = max([len(opt.description) for opt in cpu_options]) + 2

        # Create choices for CPU sizes
        choices = [
            Choice(
                value=opt.code,
                name=f"{opt.title:{max_title_length}} : {opt.description:{max_desc_length}} : {opt.price_tag}",
            )
            for opt in cpu_options
        ]

        compute_size = await inquirer.select(
            message=f"Select compute for your {title}:",
            choices=choices,
            default=compute_size,
            style=style,
        ).execute_async()

    save_config({"compute_size": compute_size})

    return compute_size


async def env_flow() -> Tuple[str, Optional[str], Optional[Dict[str, str]]]:
    """
    Ask user to select environment variables configuration.
    Returns:
        Tuple containing:
        - env_type: "file" or "values"
        - env_file: filename if env_type == "file", None otherwise
        - env_values: dict of values if env_type == "values", None otherwise
    """

    job_type = load_config("job_type")
    if job_type == JobTypeEnum.LAB:
        env_type = "values"
        env_file = None
        env_values = {}

        # Save the configuration
        save_config({"env_type": env_type, "env_file": env_file, "env_values": env_values})

        return env_type, env_file, env_values

    console.print(Panel("[bold]Environment variables (optional)[/]", expand=False))

    env_type = load_config("env_type")
    env_file = load_config("env_file")

    # Find all .env* files in the current directory
    env_files = glob.glob(".env*")

    # Determine which options to present based on found env files
    if env_files:
        # Multiple .env files found - let user choose one or enter custom values
        choices = [Choice(value=f, name=f"Use {f} file") for f in env_files]
        choices.append(Choice(value="$custom", name="Enter manually"))

        selected = await inquirer.select(
            message="Select environment variables:",
            choices=choices,
            default=env_file if env_file in [c.value for c in choices] else choices[-1].value,
            style=style,
        ).execute_async()

    else:
        # No .env files found - collect environment variables manually
        console.print("Your application might need some environment variables.")
        console.print("They can be provided via the .env file or manually.")
        console.print(
            "[yellow]No .env files found in current directory. Provide ENV one-by-one if needed.[/]"
        )
        console.print("Format: KEY=VALUE. To finish, press ENTER")
        selected = "$custom"

    if selected == "$custom":
        env_type = "values"
        env_file = None
        env_values = await collect_env_values()
    else:
        env_type = "file"
        env_file = selected
        env_values = None

        # read env file
        env_values = parse_env_file(env_file)
        console.print(f"Environment variables will be loaded from {env_file}:")
        for key in env_values.keys():
            console.print(f"- {key}")

    console.print()

    # Save the configuration
    save_config({"env_type": env_type, "env_file": env_file, "env_values": env_values})

    return env_type, env_file, env_values


async def config_flow(status: Status, force_config: bool = False) -> dict:
    """
    Configuration Flow
    Handles all configuration settings with strict validation.
    """
    config = {}
    config_changed = False

    # Stop the status to avoid interference with questions
    status.stop()

    # Job type configuration
    job_type_value = load_config("job_type")
    if force_config or job_type_value is None:
        job_type, job_schedule = await type_flow()
        config["job_type"] = job_type.value
        config["job_schedule"] = job_schedule
        config_changed = True
    else:
        job_schedule = load_config("job_schedule")
        config["job_type"] = job_type_value
        config["job_schedule"] = job_schedule
        job_type = JobTypeEnum(job_type_value)

    # Compute size configuration (CPU/GPU)
    compute_size_value = load_config("compute_size")
    if force_config or compute_size_value is None:
        config["compute_size"] = await size_flow(job_type, force_config)
    else:
        config["compute_size"] = compute_size_value

    # Disk size configuration
    disk_size_value = load_config("disk_size")
    if force_config or disk_size_value is None:
        disk_size = await disk_flow()
        config["disk_size"] = disk_size
    else:
        config["disk_size"] = disk_size_value

    # Storage configuration
    storage_value = load_config("storage")
    if job_type != JobTypeEnum.LAB:
        if force_config or storage_value is None:
            storage = await storage_flow()
            config["storage"] = storage
        else:
            config["storage"] = storage_value
    else:
        # Do not offer storage for lab
        config["storage"] = []

    # Environment variables configuration
    env_type_value = load_config("env_type")
    if force_config or env_type_value is None:
        env_type, env_file, env_values = await env_flow()
        config["env_type"] = env_type
        config["env_file"] = env_file
        config["env_values"] = env_values
    else:
        config["env_type"] = load_config("env_type")
        config["env_file"] = load_config("env_file")
        config["env_values"] = load_config("env_values", {})

    # Services configuration
    services_value = load_config("services", None)
    if job_type == JobTypeEnum.LAB:
        # Do not offer services for lab
        config["services"] = {}

    elif force_config or services_value is None:
        base_directory = os.getcwd()
        requirements_txt_path = os.path.join(base_directory, "requirements.txt")
        pyproject_toml_path = os.path.join(base_directory, "pyproject.toml")
        pipfile_path = os.path.join(base_directory, "Pipfile")

        dependencies = {}
        if os.path.exists(pyproject_toml_path):
            dependencies = parse_dependencies(pyproject_toml_path)
        elif os.path.exists(pipfile_path):
            dependencies.update(parse_dependencies(pipfile_path))
        elif os.path.exists(requirements_txt_path):
            dependencies.update(parse_dependencies(requirements_txt_path))

        service_offers = {}
        service_keywords = {
            "redis": ["redis"],
            "postgres": [
                "psycopg",
                "asyncpg",
                "SQLAlchemy",
                "Django",
                "Peewee",
                "Tortoise",
                "Pony",
                "SQLObject",
                "pg8000",
            ],
            "clickhouse": [
                "clickhouse",
                "aiochclient",
            ],
        }
        for dependency in dependencies:
            for service, keywords in service_keywords.items():
                if any(keyword.lower() in dependency.lower() for keyword in keywords):
                    service_offers[service] = dependency
                    break

        # convert None to {} if needed
        services_value = services_value if services_value else {}
        for srv in services_value.keys():
            if srv not in service_offers:
                service_offers[srv] = None

        if service_offers:
            console.print(Panel("[bold]Backend Services (optional)[/]", expand=False))

        for service_offer, dependency in service_offers.items():
            # Ask user if they want to add service (y/N)
            if dependency:
                console.print(f"You have {dependency} in your dependencies.")
            service_choice = await inquirer.confirm(
                message=f"Do you need to install {service_offer} for your application?",
                default=service_offer in services_value.keys(),
            ).execute_async()
            if service_choice:
                services_value[service_offer] = {}
                if service_offer == "redis":
                    console.print("Note: Redis will be available at [bold]localhost:6379[/]")

                elif service_offer == "postgres":
                    console.print(
                        "Note: Postgres will be available at [bold]localhost:5432[/] \n"
                        "Use POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB environment variables to connect to the database"
                    )
                    # while config["compute_size"] in ["cpu-xs", "cpu-s"]:
                    #     console.print()
                    #     console.print(
                    #         "[yellow bold]Warning:[/] to use Postgres, choose a larger compute size (with RAM >= 2Gb)"
                    #     )
                    #     config["compute_size"] = await size_flow(job_type, True, False)

                elif service_offer == "clickhouse":
                    console.print(
                        "Note: Clickhouse will be available at [bold]localhost:9000[/] \n"
                        "Use CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_PORT, CLICKHOUSE_TCP_PORT environment variables to connect to the database"
                    )
                    while config["compute_size"] in ["cpu-xs", "cpu-s"]:
                        console.print()
                        console.print(
                            "[yellow bold]Warning:[/] to use Clickhouse, choose a larger compute size (with RAM >= 2Gb)"
                        )
                        config["compute_size"] = await size_flow(job_type, True, False)

            else:
                services_value.pop(service_offer, None)
            console.print()

        config["services"] = services_value

    # Validate the complete configuration
    try:
        validate_config(config)
    except ValueError as e:
        console.print(f"[red]Configuration error: {str(e)}[/]")
        raise click.Abort()

    # Save the full configuration
    save_config(config)

    if config_changed:
        console.print()
        console.print("[green]Configuration saved successfully[/]")
        console.print(
            "Note: You can reconfigure your application by running: [bold]omega config[/]"
        )
        console.print()

    # Start the status again
    status.start()

    return config


async def run_task_flow(status: Status, fixed_agent_id: Optional[str] = None) -> str:
    """
    Steps:
    1. Inspect task status
    2. Create task if not exists
    3. If task is OFF, sync files and enable task
    4. If task is ON, check job status and offer to run immediately
    """
    status.update("[bold cyan]Checking the scheduled job...[/]")

    task_id = get_task_id(raise_error=False)
    task_info = await inspect_task(task_id)

    if not task_id or not task_info.task_status:
        console.print("- Scheduled job not found. Creating...")
        status.update("[bold cyan]Creating the scheduled job...[/]")

        task_info = await api.init_task_api(
            size=load_config("compute_size"),
            disk_size=load_config("disk_size"),
            storage=load_config("storage"),
            environment=get_environment_variables(),
            services=load_config("services"),
            schedule=load_config("job_schedule"),
            setup_cmd=load_script("setup.sh"),
            run_cmd=load_script("task.sh"),
            build_cmd=load_script("build.sh"),
            fixed_agent_id=fixed_agent_id,
        )
        task_id = task_info.task_id
        save_config({"task_id": task_id})
        task_info = await inspect_task(task_id)

    if task_info.task_status == TaskStatusEnum.OFF:
        console.print("- Scheduled job initialized. Enabling...")

        # sync
        job_type = JobTypeEnum(load_config("job_type"))
        if job_type == JobTypeEnum.JOB:
            files_are_synced = await sync_flow(status, sync_type="task", operations="upload")
            if not files_are_synced:
                raise KeyboardInterrupt

        status.update("[bold cyan]Enabling the scheduled job...[/]")
        task_info = await api.enable_task_api(
            task_id,
            schedule=load_config("job_schedule"),
            setup_cmd=load_script("setup.sh"),
            run_cmd=load_script("task.sh"),
            build_cmd=load_script("build.sh"),
            fixed_agent_id=fixed_agent_id,
        )

    if task_info.task_status == TaskStatusEnum.ON:
        console.print("- Scheduled job enabled")
        console.print("- Note: You can disable your job by running: [bold]omega stop[/]")
        console.print()
        if task_info.job_status != JobStatusEnum.RUNNING:
            # ask user to start now
            task_action = await ask(
                status,
                "Do you want to run your job now?",
                [
                    ("yes", "Yes, run it now"),
                    ("no", "No, wait for schedule"),
                ],
                timeout=30,
            )
            if task_action == "no":
                return

            task_info = await api.run_task_api(task_id)
            console.print("- Scheduled job initialized")
            max_wait_time = 60  # sec
            sleep_time = 3  # sec
            start_time = time.time()
            while (time.time() - start_time) < max_wait_time:
                status.update("[bold cyan]Starting the job...[/]")
                await asyncio.sleep(sleep_time)
                task_info = await inspect_task(task_id)
                if task_info.job_status == JobStatusEnum.RUNNING:
                    break

    if task_info.task_status == TaskStatusEnum.ON and task_info.job_status == JobStatusEnum.RUNNING:
        await watch_flow(status)


async def run_agent_flow(status: Status):
    """
    Steps:
    1. Inspect agent status
    2. Create agent if not exists
    3. Wait for IDLE status (break if DEAD)
    3. Sync files
    4. Run process
    """
    status.update("[bold cyan]Checking the server (runtime environment)...[/]")

    # get agent status
    agent_id = get_agent_id(raise_error=False)
    agent_info = await inspect_agent(agent_id)
    job_type = JobTypeEnum(load_config("job_type"))

    if (
        not agent_id
        or not agent_info.agent_status
        or agent_info.agent_status == AgentStatusEnum.DEAD
    ):
        console.print("- Server not found. Creating...")

        status.update("[bold cyan]Checking the name...[/]")
        fixed_name = load_config("fixed_name", None)
        valid_fixed_name = await validate_fixed_name(fixed_name)
        if not valid_fixed_name:
            console.print(
                f"[red]Name {fixed_name} is unavailable or incorrect. Please try another name.[/]"
            )
            raise click.Abort()

        status.update("[bold cyan]Creating the server...[/]")
        agent_info = await api.init_agent_api(
            load_config("compute_size"),
            load_config("disk_size"),
            load_config("storage"),
            get_environment_variables(),
            load_config("services"),
            JobTypeEnum(load_config("job_type")),
            load_script("setup.sh"),
            load_script("run.sh"),
            load_script("build.sh"),
            load_config("fixed_name"),
        )
        agent_id = agent_info.agent_id
        save_config({"agent_id": agent_id})
        console.print("- Server initialized. Starting...")

        while agent_info.agent_status != AgentStatusEnum.INIT:
            await asyncio.sleep(1)
            agent_info = await inspect_agent(agent_id)

    status_text = None
    while agent_info.agent_status == AgentStatusEnum.INIT:
        status.update("[bold cyan]Starting the server...[/]")

        await asyncio.sleep(1)
        agent_info = await inspect_agent(agent_id)

        if (
            agent_info.agent_status_text
            and agent_info.agent_status_text != status_text
            and agent_info.agent_status in [AgentStatusEnum.INIT]
        ):
            status_text = agent_info.agent_status_text
            console.print(f"- {status_text}")

        # Break if status becomes DEAD during initialization
        if agent_info.agent_status == AgentStatusEnum.DEAD:
            console.print("[red]Server launch failed[/]")
            print_logs("Server Logs", agent_info.agent_logs)
            raise click.Abort()

    if agent_info.agent_status == AgentStatusEnum.IDLE:
        files_are_synced = await sync_flow(status, sync_type="agent", operations="upload")
        if not files_are_synced:
            raise KeyboardInterrupt

        agent_info = await api.run_agent_api(agent_id)
        console.print("- Server ready. Starting application...")

    while agent_info.agent_status != AgentStatusEnum.BUSY:
        status.update("[bold cyan]Starting the application...[/]")
        await asyncio.sleep(1)
        agent_info = await inspect_agent(agent_id, get_logs=True)
        # Break if status becomes DEAD during initialization
        if agent_info.agent_status == AgentStatusEnum.DEAD:
            console.print("[red]Application failed[/]")
            print_logs("Agent Logs", agent_info.agent_logs)
            raise click.Abort()
        if agent_info.job_logs and not load_config("job_schedule") and job_type != JobTypeEnum.LAB:
            for log in agent_info.job_logs:
                console.print(log, highlight=False, markup=False, end="")

    if agent_info.agent_status == AgentStatusEnum.BUSY:
        console.print("- Application is running")
        console.print("- Note: You can stop your application by running: [bold]omega stop[/]")
        console.print()
        agent_info = await inspect_agent(agent_id, get_logs=True)
        if agent_info.job_url:
            console.print(Panel(f"Application URL: {agent_info.job_url}", expand=False))
            console.print()
        if not load_config("job_schedule") and job_type != JobTypeEnum.LAB:
            console.print(
                "Note: You can watch the logs by running: [bold]omega watch[/] or [bold]omega logs[/]"
            )
            console.print()
            await watch_flow(status)


async def run_flow(status: Status) -> None:
    """
    Run Flow - Initiates and starts an application based on its type.
    Decision Tree:
    - Lab Application: RUN_AGENT_PROCEDURE
    - API Only Application: RUN_AGENT_PROCEDURE
    - API + Scheduled Job: RUN_AGENT_PROCEDURE + RUN_TASK_PROCEDURE
    - One-time Job: RUN_AGENT_PROCEDURE
    - Scheduled Job: RUN_TASK_PROCEDURE
    """
    await config_flow(status)

    job_type = JobTypeEnum(load_config("job_type"))
    job_schedule = load_config("job_schedule")

    # Scheduled Job - only needs task procedure
    if job_type == JobTypeEnum.LAB:
        await run_agent_flow(status)

    if job_type == JobTypeEnum.API and not job_schedule:
        # API Only Application
        await run_agent_flow(status)

    if job_type == JobTypeEnum.API and job_schedule:
        # API + Scheduled Job
        await run_agent_flow(status)
        await run_task_flow(status, get_agent_id())

    if job_type == JobTypeEnum.JOB and not job_schedule:
        # One-time Job
        await run_agent_flow(status)

    if job_type == JobTypeEnum.JOB and job_schedule:
        # Scheduled Job
        await run_task_flow(status)


async def stop_agent_flow(status: Status, agent_id: str) -> bool:
    """
    Steps:
    1. Inspect agent status
    2. Stop running process
    3. Sync files in IDLE state
    4. Terminate agent (LAB type always terminates)
    """
    agent_info = await inspect_agent(agent_id)

    # If agent is not running, nothing to do
    if (
        not agent_info
        or not agent_info.agent_status
        or agent_info.agent_status
        not in [
            AgentStatusEnum.INIT,
            AgentStatusEnum.BUSY,
            AgentStatusEnum.IDLE,
        ]
    ):
        console.print("[green]No application to stop[/]")
        console.print()
        return True

    # Stop initizlizing agent
    if agent_info.agent_status == AgentStatusEnum.INIT:
        status.update("[bold cyan]Stopping initialization...[/]")
        await api.kill_agent_api(agent_id)
        console.print("[green]Initialization stopped[/]")
        console.print()
        return True

    # Stop running process if busy
    if agent_info.agent_status == AgentStatusEnum.BUSY:
        status.update("[bold cyan]Stopping your application...[/]")
        await api.stop_agent_api(agent_id)

        # Wait for IDLE state
        while agent_info.agent_status != AgentStatusEnum.IDLE:
            await asyncio.sleep(1)
            agent_info = await inspect_agent(agent_id)

    # Sync files in IDLE state if required
    if agent_info.agent_status == AgentStatusEnum.IDLE:
        console.print("[green]Application stopped[/]")
        console.print()
        await sync_flow(status, sync_type="agent", operations="download")

    if agent_info.job_type == JobTypeEnum.LAB:
        terminate_answer = "terminate"
    else:
        # ask user to terminate agent
        terminate_answer = await ask(
            status,
            "Do you want to terminate the server?",
            [
                ("terminate", "Yes, terminate"),
                ("keep", "No, keep it running"),
            ],
            timeout=30,
        )
    if terminate_answer == "terminate":
        status.update("[bold cyan]Terminating server...[/]")
        agent_info = await api.kill_agent_api(agent_id)

    if agent_info.agent_status == AgentStatusEnum.DEAD:
        print_costs(agent_info)
        console.print("[green]Application stopped. Server terminated[/]")
        console.print()
    elif agent_info.agent_status == AgentStatusEnum.IDLE:
        console.print("[green]Application stopped. Server still running.[/]")
        console.print()

    return True


async def stop_task_flow(status: Status, task_id: str) -> bool:
    """
    Steps:
    1. Inspect task status
    2. Handle running job
    3. Disable task
    """

    status.update("[bold cyan]Checking the scheduled job...[/]")
    task_info = await inspect_task(task_id)
    job_type = JobTypeEnum(load_config("job_type"))

    # If task is not enabled, nothing to do
    if not task_info or not task_info.task_status:
        console.print("[red]Scheduled job not found[/]")
        console.print()
        return True

    if task_info.task_status == TaskStatusEnum.ON:
        if task_info.job_status == JobStatusEnum.RUNNING:
            console.print("- Scheduled job is running. Stopping...")
            status.update("[bold cyan]Stopping the scheduled job...[/]")
            await api.stop_task_api(task_id)

        # Disable task
        console.print("- Scheduled job stopped. Disabling...")
        stop_agent = job_type == JobTypeEnum.JOB  # if API, then don't stop agent
        task_info = await api.disable_task_api(task_id, stop_agent=stop_agent)

    if task_info.task_status == TaskStatusEnum.OFF:
        console.print("- Scheduled job disabled. Syncing files...")
        await sync_flow(status, sync_type="task", operations="download")

    console.print("[green]Scheduled job cancelled[/]")
    console.print()

    if job_type == JobTypeEnum.JOB:
        print_costs(task_info)

    return True


async def stop_flow(status: Status) -> bool:
    """
    Stop Flow - Safely stops running applications and cleans up resources.
    Decision Tree:
    - Lab Application: STOP_AGENT_PROCEDURE
    - API Only Application: STOP_AGENT_PROCEDURE
    - API + Scheduled Job: STOP_TASK_PROCEDURE + STOP_AGENT_PROCEDURE
    - One-time Job: STOP_AGENT_PROCEDURE
    - Scheduled Job: STOP_TASK_PROCEDURE
    """
    status.update("[bold cyan]Stopping application...[/]")
    agent_id = get_agent_id(raise_error=False)
    task_id = get_task_id(raise_error=False)

    job_type = JobTypeEnum(load_config("job_type"))
    job_schedule = load_config("job_schedule")

    # Lab type - always terminate
    if job_type == JobTypeEnum.LAB:
        await stop_agent_flow(status, agent_id)

    # API Only - stop agent
    elif job_type == JobTypeEnum.API and not job_schedule:
        await stop_agent_flow(status, agent_id)

    # API + Scheduled Job - stop both task and agent
    elif job_type == JobTypeEnum.API and job_schedule:
        await stop_task_flow(status, task_id)
        await stop_agent_flow(status, agent_id)

    # Scheduled Job - stop agent and optionally terminate
    elif job_type == JobTypeEnum.JOB and job_schedule:
        await stop_task_flow(status, task_id)

    # One-time Job - stop agent and optionally terminate
    elif job_type == JobTypeEnum.JOB and not job_schedule:
        await stop_agent_flow(status, agent_id)


# HELPERS


async def ask(
    status: Status,
    question: str,
    answers: List[Tuple[str, str]],
    default: Optional[str] = None,
    timeout: Optional[float] = None,
) -> str:
    is_active = status._live._started

    if is_active:
        status.stop()

    select_choices = [Choice(value=answer[0], name=answer[1]) for answer in answers]

    # Determine the default choice value, ensure it exists in the choices
    default_value = default
    if default_value is None and select_choices:
        default_value = select_choices[0].value
    elif default_value not in [c.value for c in select_choices]:
        default_value = select_choices[0].value if select_choices else None

    prompt = inquirer.select(
        message=question,
        choices=select_choices,
        default=default_value,
        style=style,
    )

    user_choice = None
    try:
        if timeout is not None:
            # Wrap the async call with a timeout
            user_choice = await asyncio.wait_for(prompt.execute_async(), timeout=timeout)
        else:
            # Execute without timeout
            user_choice = await prompt.execute_async()

    except TimeoutError:
        console.print(
            f"\n[yellow]You have not selected anything. Using default value: {default_value}[/]"
        )
        user_choice = default_value
    except ValueError:
        user_choice = default_value

    if is_active:
        status.start()

    return user_choice


def make_progress_callback(progress: Progress, task_id: TaskID) -> Callable[[float], None]:
    """Create a progress callback function for tracking file transfer progress."""

    def progress_callback(bytes_transferred: float):
        progress.update(task_id, completed=bytes_transferred)

    return progress_callback


async def inspect_task(task_id: str) -> TaskStatusResponseModel:
    if not task_id:
        return TaskStatusResponseModel(task_id=task_id)

    try:
        return await api.inspect_task_api(task_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return TaskStatusResponseModel(task_id=task_id)
        else:
            raise e


def get_logs_length(watch_id: str, queue_name: str) -> int:
    log_dir = os.path.join(os.getcwd(), ".omega", "logs")
    log_file_path = os.path.join(log_dir, f"{watch_id}.{queue_name}.log")
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as f:
                return len(f.readlines())
    except Exception:
        pass

    return 0


async def inspect_agent(agent_id: str, get_logs: bool = False) -> AgentStatusResponseModel:
    if not agent_id:
        return AgentStatusResponseModel(agent_id=agent_id)

    try:
        queue_name = None
        log_start = -1
        if get_logs:
            queue_name = load_config("job_type", None)
            log_start = get_logs_length(agent_id, queue_name)

        inspect_response = await api.inspect_agent_api(agent_id, queue_name, log_start)

        # save job log to .omega/logs/<queue_name>.log
        if queue_name and inspect_response.job_logs:
            log_dir = os.path.join(os.getcwd(), ".omega", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file_path = os.path.join(log_dir, f"{agent_id}.{queue_name}.log")
            with open(log_file_path, "a") as f:
                f.write("".join(inspect_response.job_logs))
        return inspect_response
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return AgentStatusResponseModel(agent_id=agent_id)
        else:
            raise e


def get_job_title(job_type: JobTypeEnum) -> str:
    if job_type == JobTypeEnum.JOB:
        return "Job"
    elif job_type == JobTypeEnum.API:
        return "API Service"
    elif job_type == JobTypeEnum.LAB:
        return "Lab (Jupyter Notebook)"


def autodetect_build_commands() -> List[str]:
    """
    Detect build commands for the application (install dependencies)
    """
    base_directory = os.getcwd()

    requirements_txt_path = os.path.join(base_directory, "requirements.txt")
    # pyproject_toml_path = os.path.join(base_directory, "pyproject.toml")
    uv_lock_path = os.path.join(base_directory, "uv.lock")
    poetry_lock_path = os.path.join(base_directory, "poetry.lock")
    package_json_path = os.path.join(base_directory, "package.json")

    build_commands = []
    if os.path.exists(uv_lock_path):
        build_commands = ["uv sync"]
    elif os.path.exists(poetry_lock_path):
        build_commands = ["poetry install"]
    elif os.path.exists(requirements_txt_path):
        build_commands = ["pip install --no-cache-dir -r requirements.txt"]
    elif os.path.exists(package_json_path):
        package_manager = get_node_package_manager()
        build_commands = [f"{package_manager} install"]

    return build_commands


def get_node_package_manager() -> str:
    """
    Detect package manager for Node.js
    """
    base_directory = os.getcwd()
    # Check for lock files to determine package manager
    if os.path.exists(os.path.join(base_directory, "pnpm-lock.yaml")):
        package_manager = "pnpm"
    elif os.path.exists(os.path.join(base_directory, "yarn.lock")):
        package_manager = "yarn"
    elif os.path.exists(os.path.join(base_directory, "package-lock.json")):
        package_manager = "npm"
    else:
        # Default to npm if no lock file is found
        package_manager = "npm"

    return package_manager


def get_node_scripts() -> Dict[str, str]:
    """
    Get all scripts from package.json and detect package manager
    """
    base_directory = os.getcwd()
    package_json_path = os.path.join(base_directory, "package.json")
    if not os.path.exists(package_json_path):
        return {}

    with open(package_json_path, "r") as f:
        package_json = json.load(f)

    package_manager = get_node_package_manager()

    # Return scripts with package manager prefix
    package_json_scripts = package_json.get("scripts", {})
    scripts = {f"{package_manager} run {k}": v for k, v in package_json_scripts.items()}
    return scripts


def get_poetry_scripts() -> Dict[str, str]:
    """
    Get all scripts from pyproject.toml and detect package manager
    """
    base_directory = os.getcwd()
    pyproject_toml_path = os.path.join(base_directory, "pyproject.toml")
    if not os.path.exists(pyproject_toml_path):
        return {}

    with open(pyproject_toml_path, "r") as f:
        pyproject_toml = toml.load(f)

    poetry_scripts = pyproject_toml.get("tool", {}).get("poetry", {}).get("scripts", {})
    scripts = {k: v for k, v in poetry_scripts.items()}
    return scripts


async def autodetect_framework() -> str:
    """
    Detect the framework used in the application
    """
    base_directory = os.getcwd()
    requirements_txt_path = os.path.join(base_directory, "requirements.txt")
    pyproject_toml_path = os.path.join(base_directory, "pyproject.toml")
    package_json_path = os.path.join(base_directory, "package.json")

    framework = "unknown"
    if os.path.exists(requirements_txt_path):
        # Python
        with open(requirements_txt_path, "r") as f:
            requirements_content = f.read().lower()
        if "uvicorn" in requirements_content:
            framework = "uvicorn"
        elif "gunicorn" in requirements_content:
            framework = "gunicorn"
    elif os.path.exists(pyproject_toml_path):
        with open(pyproject_toml_path, "r") as f:
            pyproject_toml_content = f.read().lower()
        if "uvicorn" in pyproject_toml_content:
            framework = "uvicorn"
        elif "gunicorn" in pyproject_toml_content:
            framework = "gunicorn"

    if os.path.exists(package_json_path):
        # Node
        framework = "node"

    return framework


async def autodetect_run_commands() -> List[str]:
    """
    Detect run commands for the application
    """
    base_directory = os.getcwd()
    pyproject_toml_path = os.path.join(base_directory, "pyproject.toml")
    uv_lock_path = os.path.join(base_directory, "uv.lock")
    poetry_lock_path = os.path.join(base_directory, "poetry.lock")
    requirements_txt_path = os.path.join(base_directory, "requirements.txt")
    package_json_path = os.path.join(base_directory, "package.json")

    run_commands = []
    if (
        os.path.exists(requirements_txt_path)
        or os.path.exists(pyproject_toml_path)
        or os.path.exists(uv_lock_path)
        or os.path.exists(poetry_lock_path)
    ):
        # python
        framework = await autodetect_framework()
        main_file = "main"
        app_name = "app"
        port = 8008
        host = "0.0.0.0"
        workers = 4

        if framework == "uvicorn":
            run_commands = [
                f"uvicorn --host {host} --port {port} --workers {workers} {main_file}:{app_name}"
            ]
        elif framework == "gunicorn":
            run_commands = [f"gunicorn -b {host}:{port} -w {workers} {main_file}:{app_name}"]
        else:
            run_commands = [f"python {main_file}.py"]

    if os.path.exists(package_json_path):
        # node
        package_manager = get_node_package_manager()
        default_script = f"{package_manager} run start"
        run_commands = [default_script]

    return run_commands


def autodetect_task_commands() -> List[str]:
    """
    Detect commands for scheduled task
    """
    base_directory = os.getcwd()
    pyproject_toml_path = os.path.join(base_directory, "pyproject.toml")
    uv_lock_path = os.path.join(base_directory, "uv.lock")
    poetry_lock_path = os.path.join(base_directory, "poetry.lock")
    requirements_txt_path = os.path.join(base_directory, "requirements.txt")
    package_json_path = os.path.join(base_directory, "package.json")

    task_commands = []
    if (
        os.path.exists(requirements_txt_path)
        or os.path.exists(pyproject_toml_path)
        or os.path.exists(uv_lock_path)
        or os.path.exists(poetry_lock_path)
    ):
        task_commands = ["python main.py"]
    if os.path.exists(package_json_path):
        package_manager = get_node_package_manager()
        task_commands = [f"{package_manager} run start"]

    return task_commands


async def autodetect_job_type() -> JobTypeEnum:
    """Detect the job type based on the files in the current directory.

    Returns:
        JobTypeEnum: The job type.
    """

    framework = await autodetect_framework()
    if framework in ["uvicorn", "gunicorn", "node"]:
        return JobTypeEnum.API
    else:
        return JobTypeEnum.JOB


def get_environment_variables() -> Dict[str, str]:
    """
    Get environment variables based on env_type config setting.

    Returns:
        Dictionary of environment variables
    """
    env_type = load_config("env_type")
    env_file = load_config("env_file")
    env_values = load_config("env_values", {})

    if not env_type:
        return {}

    if env_type == "file":
        if not env_file:
            console.print("[yellow]Warning: env_type is 'file' but no env_file specified[/]")
            return {}
        return parse_env_file(env_file)
    elif env_type == "values":
        return env_values
    else:
        console.print(f"[yellow]Warning: Unknown env_type '{env_type}'[/]")
        return {}


def parse_env_file(file_path: str) -> Dict[str, str]:
    """
    Parse a .env file and return key-value pairs.

    Args:
        file_path: Path to the .env file

    Returns:
        Dict of environment variable key-value pairs
    """
    env_vars = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split("=", 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value
    except Exception as e:
        console.print(f"[red]Error parsing {file_path}: {str(e)}[/]")

    return env_vars


async def ask_env_var(default: str) -> Tuple[str, str]:
    while True:
        key_value = await inquirer.text(
            message="Environment variable (format: KEY=VALUE):",
            style=style,
            default=default,
        ).execute_async()

        if not key_value:
            return None, None

        parts = key_value.split("=", 1)
        if len(parts) != 2 or not parts[0].strip():
            console.print("[red]Invalid format. Please use KEY=VALUE format.[/]")
        else:
            break

    return parts[0].strip(), parts[1].strip()


async def collect_env_values() -> Dict[str, str]:
    """
    Collect environment variables from user input.

    Args:
        existing_values: Existing environment variables to start with

    Returns:
        Dict of environment variable key-value pairs
    """

    new_values = {}
    old_values = load_config("env_values", {})

    # First, process existing values if any
    if old_values:
        for key, value in old_values.items():
            new_key, new_value = await ask_env_var(f"{key}={value}")
            if new_key is not None:
                new_values[new_key] = new_value

    while True:
        new_key, new_value = await ask_env_var("")
        if new_key is None:
            break
        new_values[new_key] = new_value

    return new_values


def get_task_id(raise_error: bool = True) -> str:
    task_id = load_config("task_id")
    if not task_id:
        if raise_error:
            console.print("[bold red]No task found[/]")
            raise click.Abort()
        else:
            return None
    return task_id


def get_agent_id(raise_error: bool = True) -> str:
    agent_id = load_config("agent_id")
    if not agent_id:
        if raise_error:
            console.print("[bold red]No server found[/]")
            raise click.Abort()
        else:
            return None
    return agent_id


def print_costs(info: Union[AgentStatusResponseModel, TaskStatusResponseModel]):
    if info.compute_cost is not None or info.storage_cost is not None:
        console.print()
        console.print("[bold]Billing:[/]")
    if info.compute_cost is not None:
        console.print(f"Compute: ${info.compute_cost:.4f}")
    if info.storage_cost is not None:
        console.print(f"Storage: ${info.storage_cost:.4f}")


def print_logs(title: str, logs: List[str]):
    if not logs:
        return

    indent = " " * 4
    console.print(f"{title.title()}:")
    if len(logs) > 0:
        console.print(indent + "...", highlight=False, markup=False)
    for line in logs:
        console.print(indent + line.strip(), highlight=False, markup=False)


def display_environment_variables(env_vars: Dict[str, str], header: str = None) -> None:
    """
    Display environment variables with masked values for sensitive information.

    Args:
        env_vars: Dictionary of environment variables
        header: Optional header text to display before variables
    """
    if not env_vars:
        console.print("[yellow]No environment variables defined.[/]")
        return

    if header:
        console.print(f"[cyan]{header}[/]")

    for key, value in env_vars.items():
        # Mask sensitive values
        masked_value = value[:3] + "****" if len(value) > 6 else "****"
        console.print(f"  {key}={masked_value}")


async def validate_fixed_name(fixed_name: str) -> bool:
    if not fixed_name:
        return True

    # check if this name is dns-compliant
    if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$", fixed_name):
        return False

    # check if this name is not reserved
    agent_id = load_config("agent_id", None)
    valid_fixed_name = await api.check_fixed_name_api(fixed_name, agent_id)
    return valid_fixed_name


def validate_cron_format(cron_string: str) -> bool:
    """
    Validate if a string is in proper cron format.

    Args:
        cron_string: The cron string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # First validate with croniter
        croniter(cron_string, datetime.now())

        # Then validate with celery cron converter
        cron_to_celery_cron(cron_string)
        return True
    except (ValueError, Exception):
        return False


def validate_config(config: dict) -> bool:
    """
    Validate configuration
    Returns True if valid, raises ValueError with description if invalid.
    """
    job_type = config.get("job_type")
    job_schedule = config.get("job_schedule")
    compute_size = config.get("compute_size")
    disk_size = config.get("disk_size")
    services = config.get("services")
    storage = config.get("storage")

    # Common validations
    if not compute_size:
        raise ValueError("compute_size is required for all application types")
    if not disk_size:
        raise ValueError("disk_size is required for all application types")
    # if not storage:
    #     raise ValueError("storage configuration is required for all application types")

    # Type-specific validations
    if job_type == JobTypeEnum.LAB.value:
        if job_schedule:
            raise ValueError("job_schedule must be empty for Lab applications")
        if services:
            raise ValueError("services are not available for Lab applications")
        if storage:
            raise ValueError("storage is not available for Lab applications")

    elif job_type == JobTypeEnum.API.value:
        # job_schedule is optional for API type
        if job_schedule and not validate_cron_format(job_schedule):
            raise ValueError(
                "If provided, job_schedule must be in cron format for API applications"
            )

    elif job_type == JobTypeEnum.JOB.value:
        if job_schedule and not validate_cron_format(job_schedule):
            raise ValueError(
                "job_schedule must be either empty or in cron format for Job applications"
            )

    else:
        raise ValueError(f"Invalid job_type: {job_type}")

    return True


def detect_package_manager() -> str:
    """
    Detect the primary package manager for the current project.
    Returns:
        str: The detected package manager ('uv', 'poetry', 'pip', 'pnpm', 'yarn', 'npm', or None if not detected)
    """
    base_directory = os.getcwd()

    # Check for Python package managers
    if os.path.exists(os.path.join(base_directory, "uv.lock")):
        return "uv"
    elif os.path.exists(os.path.join(base_directory, "poetry.lock")):
        return "poetry"
    # elif os.path.exists(os.path.join(base_directory, "pyproject.toml")):
    #     return "poetry"
    elif os.path.exists(os.path.join(base_directory, "requirements.txt")):
        return "pip"

    # Check for Node.js package managers
    if os.path.exists(os.path.join(base_directory, "package.json")):
        if os.path.exists(os.path.join(base_directory, "pnpm-lock.yaml")):
            return "pnpm"
        elif os.path.exists(os.path.join(base_directory, "yarn.lock")):
            return "yarn"
        elif os.path.exists(os.path.join(base_directory, "package-lock.json")):
            return "npm"
        else:
            return "npm"  # Default to npm if package.json exists but no lock file

    return None


if __name__ == "__main__":
    cli()
