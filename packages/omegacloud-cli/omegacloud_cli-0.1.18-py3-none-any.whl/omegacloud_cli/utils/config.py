import os
from typing import List, Optional

import yaml


def update_config():
    config_dir = ".omega"
    public_file = os.path.join(config_dir, "config.yaml")
    secret_file = os.path.join(config_dir, "secret.yaml")

    cfg = load_config()

    public_config = {k: v for k, v in cfg.items() if k != "apikey"}
    secret_config = {k: v for k, v in cfg.items() if k == "apikey"}

    with open(public_file, "w") as f:
        yaml.dump(public_config, f)

    with open(secret_file, "w") as f:
        yaml.dump(secret_config, f)


def load_config(key: Optional[str] = None, default: Optional[str] = None):
    config_dir = ".omega"
    config_files = [
        os.path.join(config_dir, "secret.yaml"),
        os.path.join(config_dir, "config.yaml"),
    ]

    # Default values
    config = {"platform_url": "https://platform.omegacloud.ai"}

    try:
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    data = yaml.safe_load(f)
                if data:
                    config.update(data)

    except (FileNotFoundError, yaml.YAMLError, OSError):
        pass

    if key:
        return config.get(key, default)
    else:
        return config


def save_config(config: dict):
    config_dir = ".omega"
    config_file = os.path.join(config_dir, "config.yaml")

    # Ensure directory exists
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        # Create .gitignore file in the config directory
        with open(os.path.join(config_dir, ".gitignore"), "w") as f:
            f.write("secret.yaml\n")

    cfg = load_config()
    cfg.update(config)

    with open(config_file, "w") as f:
        yaml.dump(cfg, f)

    update_config()


def save_script(filename: str, content: List[str] = []):
    """Write content to a shell script file with proper permissions."""
    config_dir = ".omega"
    filepath = os.path.join(config_dir, filename)
    if content:
        with open(filepath, "w") as f:
            f.write("#!/bin/bash\n\n")
            for line in content:
                f.write(f"{line}\n")
        os.chmod(filepath, 0o755)  # Make the script executable
    elif os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass


def load_script(filename: str) -> List[str]:
    config_dir = ".omega"
    filepath = os.path.join(config_dir, filename)
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r") as f:
            all_lines = f.readlines()
    except Exception as e:
        print(f"Error loading script {filename}: {e}")
        return []

    # Filter out empty lines and comments, strip whitespace
    lines = []
    for line in all_lines:
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)

    return lines
