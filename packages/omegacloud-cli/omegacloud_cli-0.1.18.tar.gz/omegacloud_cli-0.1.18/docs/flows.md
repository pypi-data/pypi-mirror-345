# Omega Platform Documentation

## 1. Overview

### 1.1 Purpose

This document describes the Omega platform's application types, components, and operational flows for managing cloud-based applications and tasks.

### 1.2 Key Concepts

- **Application Type**: Defines how the application runs and interacts with the platform
- **Agent**: A runtime environment that executes processes
- **Task**: A record containing schedule information for recurring jobs
- **Job**: An abstraction of a running process within an agent

### 1.3 Application Types

1. **Lab**

   - Purpose: Provides Jupyter notebook environment
   - Components: Jupyter server + file synchronization
   - Configuration Requirements:
     - job_type: LAB
     - compute_size
     - disk_size

2. **API Only**

   - Purpose: Runs continuous API service
   - Components: API server + file synchronization
   - Configuration Requirements:
     - job_type: API
     - job_schedule: empty!
     - compute_size
     - disk_size
     - storage

3. **API + Scheduled Job**

   - Purpose: Combines API service with scheduled tasks
   - Components: API server + scheduler + file synchronization
   - Configuration Requirements:
     - job_type: API
     - job_schedule: non-empty: cron format
     - compute_size
     - disk_size
     - storage

4. **One-time Job**

   - Purpose: Executes single computational task
   - Components: Job executor + file synchronization
   - Configuration Requirements:
     - job_type: JOB
     - job_schedule: empty!
     - compute_size
     - disk_size
     - storage

5. **Scheduled Job**
   - Purpose: Executes recurring computational tasks
   - Components: Scheduler + file synchronization
   - Configuration Requirements:
     - job_type: JOB
     - job_schedule: non-empty: cron format
     - compute_size
     - disk_size
     - storage

## 2. User Interface

### 2.1 CLI Commands

The Omega platform provides a command-line interface where each command maps to a specific operational flow:

| Command         | Flow         | Purpose                                  |
| --------------- | ------------ | ---------------------------------------- |
| `omega run`     | Run Flow     | Start application based on configuration |
| `omega stop`    | Stop Flow    | Safely stop running applications         |
| `omega inspect` | Inspect Flow | Check status of agent/task               |
| `omega sync`    | Sync Flow    | Synchronize files with server            |
| `omega watch`   | Watch Flow   | Stream or retrieve logs                  |
| `omega config`  | Config Flow  | Configure application settings           |

### 2.3 Command Behavior

Each command initiates its corresponding flow and follows these principles:

- Idempotent execution
- Graceful interruption handling
- Automatic recovery
- Clear status feedback

When interrupted (e.g., by Ctrl+C), commands can be safely rerun and will:

1. Analyze current state
2. Skip completed steps
3. Resume from last successful point
4. Continue normal execution

## 3. Core Components

### 3.1 Agent

A runtime environment that executes processes.

#### Status Lifecycle

```ascii
                    ┌────────────────────┐
                    │        INIT        │
                    │  (Initializing)    │
                    └────────┬───────────┘
                             │
                             ▼
           ┌─────────────────────────────────┐
           │                                 │
           ▼                                 │
    ┌────────────┐                   ┌────────────┐
    │    IDLE    │ ◄─────────────►   │    BUSY    │
    │(No Process)│                   │(Processing)│
    └────────────┘                   └────────────┘
           │                                 │
           │                                 │
           ▼                                 ▼
                    ┌────────────┐
                    │    DEAD    │
                    │(Terminated)│
                    └────────────┘
```

- **INIT**: Initial unresponsive state during setup
- **IDLE**: Responsive state, no active process
- **BUSY**: Responsive state, process running
- **DEAD**: Terminal unresponsive state

Status Transitions:

- INIT → IDLE: Successful initialization
- INIT → DEAD: Failed initialization
- IDLE ↔ BUSY: Process start/stop
- IDLE → DEAD: Agent termination
- BUSY → DEAD: Agent termination

### 3.2 Task

A record for scheduled operations.

States:

- **ON**: Task is enabled and scheduled
- **OFF**: Task is disabled

### 3.3 Job

Process abstraction within an agent.

States:

- **CREATED**: Job is initialized
- **RUNNING**: Job is executing
- **STOPPED**: Job has completed or been stopped

## 4. Operational Flows and Procedures

### 4.1 Core Concepts

- **Flow**: A high-level user operation (e.g., Run Flow, Stop Flow)
- **Procedure**: A specific sequence of actions within a flow (e.g., AGENT_RUN_PROCEDURE)
- **Recovery**: All flows and procedures are designed to be resumable after interruption by analyzing current states

### 4.2 Primary Flows

#### 4.2.1 Run Flow

Purpose: Initiates and starts an application based on its type.

Decision Tree:

```ascii
Run Flow
├── Lab Application
│   └── RUN_AGENT_PROCEDURE
├── API Only Application
│   └── RUN_AGENT_PROCEDURE
├── One-time Job
│   └── RUN_AGENT_PROCEDURE
├── API + Scheduled Job
│   ├── RUN_AGENT_PROCEDURE
│   └── RUN_TASK_PROCEDURE
└── Scheduled Job
    └── RUN_TASK_PROCEDURE
```

#### 4.2.2 Stop Flow

Purpose: Safely stops running applications and cleans up resources.

Decision Tree:

```ascii
Stop Flow
├── Lab Application
│   └── STOP_AGENT_PROCEDURE
├── API Only Application
│   └── STOP_AGENT_PROCEDURE
├── One-time Job
│   └── STOP_AGENT_PROCEDURE
├── API + Scheduled Job
│   ├── STOP_TASK_PROCEDURE
│   └── STOP_AGENT_PROCEDURE
└── Scheduled Job
    └── STOP_TASK_PROCEDURE
```

### 4.3 Procedures

#### 4.3.1 RUN_AGENT_PROCEDURE

Purpose: Initializes and starts an agent with the required process.

Steps:

1. Inspect agent status

   - If DEAD/None: Initialize new agent
   - If INIT: Wait for IDLE status
   - If BUSY: Already running
   - If IDLE: Proceed to sync

2. Wait for IDLE status

   - Continuously inspect until status is IDLE
   - Break if status becomes DEAD
   - Can be interrupted (Ctrl+C) and resumed

3. Sync files

   - Execute SYNC_AGENT_PROCEDURE for Lab/API/One-time Job
   - Execute SYNC_TASK_PROCEDURE for Scheduled Tasks
   - Must complete successfully

4. Run process
   - Execute agent/run API
   - Wait for BUSY status
   - Start WATCH_LOGS_PROCEDURE if not LAB type

Error Handling:

- API errors (400/500): Terminate procedure
- Network errors: Retry with exponential backoff
- Interruption: Safe to resume from last successful step

#### 4.3.2 STOP_AGENT_PROCEDURE

Purpose: Safely stops an agent and its processes.

Steps:

1. Inspect agent status

   - If DEAD/None: Nothing to do
   - If INIT: Wait for IDLE then proceed
   - If BUSY/IDLE: Proceed with stop

2. Stop running process

   - Execute agent/stop API
   - Wait for IDLE status
   - Can be interrupted and resumed

3. Sync files in IDLE state

   - Execute SYNC_AGENT_PROCEDURE
   - Must complete successfully

4. Terminate agent (optional)
   - If LAB type: Always terminate
   - Other types: Ask user
   - Execute agent/kill API if confirmed

#### 4.3.3 RUN_TASK_PROCEDURE

Purpose: Initializes and starts a scheduled task.

Steps:

1. Inspect task status

   - If None: Initialize new task
   - If OFF: Enable task
   - If ON: Check job status

2. Enable task if OFF

   - Execute SYNC_TASK_PROCEDURE
   - Call task/enable API
   - Wait for ON status
   - Continue to check job status

3. Check job status

   - If not RUNNING: Ask to run immediately
   - If user confirms: Execute task/run API

Error Handling:

- Task creation failures: Terminate procedure
- Enable failures: Retry with exponential backoff
- Run failures: Report error, task remains enabled

#### 4.3.4 STOP_TASK_PROCEDURE

Purpose: Safely stops a running task.

Steps:

1. Inspect task status

   - If OFF/None: Nothing to do
   - If ON: Check job status

2. Handle running job (If job status is RUNNING)

   - If job status RUNNING: Ask to stop
   - If confirmed: Execute task/stop API
   - Wait until job status is STOPPED

3. Disable task
   - Execute SYNC_TASK_PROCEDURE
   - Call task/disable API
   - Verify OFF status

#### 4.3.5 File Synchronization Procedures

##### 4.3.5.1 SYNC_AGENT_PROCEDURE

Purpose: Synchronizes files between client and agent.

Steps:

1. Create client snapshot

   - Scan local directory
   - Create FilesSnapshotModel

2. Get sync actions

   - Call agent/sync API
   - Receive FilesSyncModel

3. Execute sync actions
   - Upload required files to agent
   - Download required files from agent
   - Verify sync completion

Error Handling:

- Partial sync: Resume from last successful file
- Network errors: Retry individual files
- Conflicts: Agent version takes precedence

##### 4.3.5.2 SYNC_TASK_PROCEDURE

Purpose: Synchronizes files between client and task cache.

Steps:

1. Create client snapshot

   - Scan local directory
   - Create FilesSnapshotModel

2. Get sync actions

   - Call task/sync API
   - Receive FilesSyncModel

3. Execute sync actions
   - Upload required files to task cache
   - Download required files from task cache
   - Verify sync completion

Error Handling:

- Partial sync: Resume from last successful file
- Network errors: Retry individual files
- Conflicts: Server cache version takes precedence

#### 4.3.6 Log Watching Procedures

##### 4.3.6.1 WATCH_AGENT_LOGS_PROCEDURE

Purpose: Retrieves or streams logs from agent processes based on agent status.

Prerequisites:

- For streaming logs:
  - Agent must be in IDLE or BUSY status
  - Agent must be responsive
- For one-time log retrieval:
  - Agent in DEAD or None status
  - Or agent is unresponsive

Steps:

1. Inspect agent status
   - If IDLE/BUSY:
     - Connect to agent watch API
     - Stream logs continuously
     - Handle disconnections with reconnect
   - If DEAD/None:
     - Call agent/logs API
     - Retrieve cached logs
     - One-time API call without streaming

Error Handling:

- Connection lost during streaming: Attempt reconnect
- Agent becomes unresponsive: Switch to one-time retrieval
- API errors: Report error and retry with exponential backoff

##### 4.3.6.2 WATCH_TASK_LOGS_PROCEDURE

Purpose: Retrieves logs from task executions.

Prerequisites:

- Task ID must exist
- No streaming available for tasks (always one-time retrieval)

Steps:

1. Inspect task status

   - If task exists: Proceed with log retrieval
   - If no task: Report error

2. Retrieve logs
   - Call task/logs API
   - One-time API call
   - Returns complete log history for the task

Error Handling:

- Task not found: Report error
- API errors: Retry with exponential backoff
- Partial log retrieval: Attempt to retrieve remaining logs

### 4.4 Flow Recovery

All flows and procedures are designed to be stateless and recoverable:

1. Recovery Mechanism

   - Each step checks current state
   - Skips completed steps
   - Resumes from last successful point

2. Example Recovery Scenario:

```ascii
Run Flow Interrupted
├── Agent Status: INIT
│   └── Resume: Wait for IDLE
├── Agent Status: IDLE
│   └── Resume: Start sync
├── Agent Status: BUSY
│   └── Resume: Start watch
```

3. State Determination
   - No persistent state needed
   - All decisions based on current status
   - Idempotent operations

## 5. Configuration Management

### 5.1 Configuration File

Location: `.omega/config.yaml`

#### 5.1.1 Configuration Keys

1. Application Identification

   - `agent_id`: UUID of active agent (or None)
   - `task_id`: UUID of active task (or None)
   - `job_type`: Application type (LAB/API/JOB)
   - `job_schedule`: Cron format string for scheduled jobs. Empty for non-scheduled job.

2. Resource Configuration

   - `compute_size`: Compute resource code
   - `disk_size`: Storage size in GB
   - `storage`: List of shared storage names

3. Environment Configuration

   - `env_type`: "values" or "file"
   - `env_file`: Environment file name (e.g., ".env")
   - `env_values`: Dictionary of environment variables

4. Authentication
   - `apikey`: Bearer token for API authentication

#### 5.1.2 Configuration Requirements by Application Type

1. Lab Application

   ```yaml
   job_type: lab
   compute_size: <required>
   disk_size: <required>
   storage: <required>
   job_schedule: <required>, <empty>
   ```

2. API Only

   ```yaml
   job_type: api
   job_schedule: <required>, <empty>
   compute_size: <required>
   disk_size: <required>
   storage: <required>
   ```

3. API + Scheduled Job

   ```yaml
   job_type: api
   job_schedule: <cron-format>
   compute_size: <required>
   disk_size: <required>
   storage: <required>
   ```

4. One-time Job

   ```yaml
   job_type: job
   job_schedule: <required>, <empty>
   compute_size: <required>
   disk_size: <required>
   storage: <required>
   ```

5. Scheduled Job
   ```yaml
   job_type: job
   job_schedule: <cron-format>
   compute_size: <required>
   disk_size: <required>
   storage: <required>
   ```

### 5.2 Configuration Rules

1. Modification Rules

   - Configuration cannot be modified while processes are running
   - Must stop all running processes before reconfiguration
   - New configuration takes effect on next run
   - Configuration is not supposed to be changed manually

2. Storage Rules

   - Configuration stored in `.omega/config.yaml`
   - Directory created if not exists
   - `.gitignore` automatically created

3. Environment Variables
   - Can be specified directly in config or in file
   - File-based vars take precedence
   - Supports both development and production configs

## 6. Security and Authentication

### 6.1 Authentication

- Bearer token authentication required for all API calls
- Token provided via `apikey` configuration
- No token expiration implemented
- Failed authentication redirects to login flow

### 6.2 API Security

- All API calls use HTTPS
- Rate limiting may be implemented
- No session persistence
- Token must be protected by user

## 7. Best Practices

### 7.1 Application Management

1. User picks the appropriate application type
2. User picks the resources based on application's needs
3. Use environment files for sensitive data
4. Implement proper error handling in applications

### 7.2 Operation Management

1. Allow procedures to complete when possible
2. Use Ctrl+C for safe interruption
3. Verify status before critical operations

### 7.3 File Synchronization

1. Use `.gitignore` for excluded files
2. Minimize unnecessary file transfers
3. Verify successful sync before operations
4. Handle large files appropriately

## 8. Troubleshooting

### 8.1 Recovery Procedures

1. Interrupted Operations

   - Restart the flow
   - System will resume automatically
   - Verify final state

2. Failed Operations
   - Check error messages
   - Verify configuration
   - Ensure prerequisites met
   - Retry operation
