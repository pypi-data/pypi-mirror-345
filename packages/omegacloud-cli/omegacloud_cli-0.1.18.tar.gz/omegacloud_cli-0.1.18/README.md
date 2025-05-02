# Omega CLI

OmegaCloud: One-click platform for AI-apps deployment.

## Installation

You can install OmegaCloud CLI using pip:

```bash
pip install omegacloud-cli
```

After installation, the `omega` command becomes available.

## Configuration

Configuration of your project starts automatically during the first run.
You can manually start configuration (or update config):

```bash
# Config
omega config
```

To get a token, please visit https://omegacloud.ai/user

You will be asked for token during the first run.
You can manually set a token for your project:

```bash
# Login
omega login
```

## Usage

```bash
# Run a project / Deploy an app / Schedule a task
omega run

# Check the status of your application/scheduled task
omega inspect (the same as "omega status")

# Watch logs of your application/scheduled task
omega watch (the same as "omega log")

# Stop the application / cancel scheduled task
omega stop

# Syncronize files between your local project's folder and server
omega sync

```

## Requirements

- Registration on omegacloud.ai
- Python 3.8 or higher
