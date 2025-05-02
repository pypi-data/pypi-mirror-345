import os  # Import os to check file existence
import re  # Import re for requirements.txt parsing fallback
import warnings

import toml
from packaging.requirements import Requirement


def _parse_requirement_string(req_string):
    """
    Parses a single requirement string into (name, specifier).
    Returns (None, None) if parsing fails.
    """
    if not isinstance(req_string, str):
        warnings.warn(f"Requirement must be a string, got: {type(req_string)}")
        return None, None

    name = None
    spec = "*"  # Default specifier

    try:
        req = Requirement(req_string)
        name = req.name
        # Use '*' if specifier is empty, otherwise convert specifier set to string
        spec = str(req.specifier) if req.specifier else "*"
    except Exception as e:
        warnings.warn(
            f"Could not parse requirement '{req_string}' robustly using `packaging` ({e}). Falling back."
        )

    # If packaging parsed partially but failed (e.g. invalid specifier), name might be set
    # Re-run fallback only if name wasn't determined by `packaging`
    if name is None:
        # Basic fallback parsing (less robust)
        match = re.match(r"^\s*([a-zA-Z0-9._-]+)", req_string)
        if match:
            name = match.group(1)
            spec_part = req_string[len(name) :].strip()
            # Very basic check for specifiers, ignores markers, extras etc.
            if any(op in spec_part for op in ["<", ">", "=", "!", "~"]):
                spec = spec_part or "*"  # Keep original spec part if found
            else:
                # If no operator found assume it's just the name or name[extra]
                spec = "*"
        else:
            # If fallback also failed
            warnings.warn(f"Fallback could not extract package name from: {req_string}")
            return None, None  # Failed to get name even with fallback

    # Only run basic fallback if packaging is unavailable OR it failed to find a name
    elif name is None:  # name is None because packaging is unavailable
        match = re.match(r"^\s*([a-zA-Z0-9._-]+)", req_string)
        if match:
            name = match.group(1)
            spec_part = req_string[len(name) :].strip()
            # Very basic check for specifiers, ignores markers, extras etc.
            if any(op in spec_part for op in ["<", ">", "=", "!", "~"]):
                spec = spec_part or "*"  # Keep original spec part if found
            else:
                # If no operator found assume it's just the name or name[extra]
                spec = "*"
        else:
            warnings.warn(f"Basic parsing could not extract package name from: {req_string}")
            return None, None  # Failed to get name

    # Ensure spec is a string, default to '*' if it ended up empty or None
    spec = spec if spec else "*"

    return name, spec


def _parse_pep621_list(dep_list, existing_deps_dict):
    """
    Helper to parse PEP 621 style lists (e.g., ["requests>=2.0", "Flask"])
    into the dict format {package_name: version_specifier}.
    Updates the provided existing_deps_dict in place.
    Uses _parse_requirement_string for parsing individual requirements.
    """
    if not isinstance(dep_list, list):
        warnings.warn(f"Expected a list of dependencies, but got {type(dep_list)}. Skipping.")
        return

    for req_string in dep_list:
        if not isinstance(req_string, str):
            warnings.warn(f"Skipping non-string item in dependency list: {req_string}")
            continue

        name, spec = _parse_requirement_string(req_string)

        if name:
            # Decide how to handle duplicates: here, we overwrite.
            existing_deps_dict[name] = spec
        # Warning about parsing failure happens inside _parse_requirement_string


# This function replaces the old get_dependencies
def parse_pyproject_toml(filepath="pyproject.toml"):
    """
    Reads dependencies from pyproject.toml, checking common locations
    for Poetry and PEP 621 standards (used by Hatch, Flit, PDM, Setuptools, UV).

    Args:
        filepath (str): Path to the pyproject.toml file. Defaults to "pyproject.toml".

    Returns:
        dict: A dictionary of {package_name: version_specifier_string}.
              Handles version extraction from Poetry's table format.
              Returns an empty dict if file not found or on parsing errors.
    """
    dependencies = {}
    if not os.path.exists(filepath):
        # Changed to Info level, not finding the file isn't necessarily an error
        print(f"Info: pyproject.toml not found at {filepath}")
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            parsed_toml = toml.load(file)

            # --- Try extracting from Poetry structure ---
            poetry_tool_config = parsed_toml.get("tool", {}).get("poetry", {})
            if isinstance(poetry_tool_config, dict):
                # 1. Poetry Main dependencies ([tool.poetry.dependencies])
                poetry_main_deps = poetry_tool_config.get("dependencies", {})
                if isinstance(poetry_main_deps, dict):
                    dependencies.update(poetry_main_deps)

                # 2. Poetry Dev dependencies (old style) ([tool.poetry.dev-dependencies])
                poetry_dev_deps_old = poetry_tool_config.get("dev-dependencies", {})
                if isinstance(poetry_dev_deps_old, dict):
                    dependencies.update(poetry_dev_deps_old)

                # 3. Poetry Group dependencies (new style) ([tool.poetry.group.*.dependencies])
                all_poetry_groups = poetry_tool_config.get("group", {})
                if isinstance(all_poetry_groups, dict):
                    for group_name, group_data in all_poetry_groups.items():
                        if isinstance(group_data, dict):
                            group_deps = group_data.get("dependencies", {})
                            if isinstance(group_deps, dict):
                                dependencies.update(group_deps)

            # --- Try extracting from PEP 621 structure ---
            project_config = parsed_toml.get("project", {})
            if isinstance(project_config, dict):
                # 4. PEP 621 Main dependencies ([project.dependencies]) - List format
                main_deps_list = project_config.get("dependencies")  # Can be None or list
                _parse_pep621_list(main_deps_list, dependencies)

                # 5. PEP 621 Optional dependencies ([project.optional-dependencies.*]) - Dict of lists
                optional_deps_dict = project_config.get("optional-dependencies", {})
                if isinstance(optional_deps_dict, dict):
                    for group_name, dep_list in optional_deps_dict.items():
                        _parse_pep621_list(dep_list, dependencies)

            # --- Optional: Add checks for other tools if needed (e.g., PDM specific) ---
            # pdm_tool_config = parsed_toml.get("tool", {}).get("pdm", {})
            # if isinstance(pdm_tool_config, dict):
            #   pdm_dev_deps = pdm_tool_config.get("dev-dependencies", {}).get("dev", []) # Example structure
            #   _parse_pep621_list(pdm_dev_deps, dependencies)

    except toml.TomlDecodeError as e:
        print(f"Error: Could not decode TOML file '{filepath}': {e}")
        return {}
    except Exception as e:
        # Catch unexpected errors during processing
        print(f"An unexpected error occurred while processing '{filepath}': {e}")
        return {}

    # --- Clean up final dictionary ---
    # 1. Remove 'python' itself if listed
    # 2. Handle Poetry's dictionary format for versions/options
    final_deps = {}
    for name, spec_info in dependencies.items():
        # Use casefold() for case-insensitive comparison for "python"
        if name.casefold() == "python":
            continue

        if isinstance(spec_info, dict):
            # Likely Poetry format: {"package": {"version": "^1.0", "optional": true}}
            # Extract the version string if available, default to "*"
            version = spec_info.get("version", "*")
            # Ensure version is a string, handle cases like {"package": "*"} which might be dict value
            final_deps[name] = str(version) if version is not None else "*"
        elif isinstance(spec_info, str):
            # Likely PEP 621 format already processed or simple Poetry version string
            final_deps[name] = spec_info
        else:
            # Handle cases where spec_info might be unexpected type (e.g., None, list)
            warnings.warn(f"Unexpected format for dependency '{name}': {spec_info}. Using '*'.")
            final_deps[name] = "*"  # Default if spec format is unknown/invalid

    return final_deps


def parse_pipfile(filepath="Pipfile"):
    """
    Reads dependencies from a Pipfile.

    Args:
        filepath (str): Path to the Pipfile. Defaults to "Pipfile".

    Returns:
        dict: A dictionary of {package_name: version_specifier_string}.
              Includes both [packages] and [dev-packages].
              Returns an empty dict if file not found or on parsing errors.
    """
    dependencies = {}
    if not os.path.exists(filepath):
        print(f"Info: Pipfile not found at {filepath}")
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            parsed_toml = toml.load(file)

            # Extract [packages]
            packages = parsed_toml.get("packages", {})
            if isinstance(packages, dict):
                dependencies.update(packages)

            # Extract [dev-packages]
            dev_packages = parsed_toml.get("dev-packages", {})
            if isinstance(dev_packages, dict):
                # Prefix dev package names? No, just merge them for now.
                # Consider if distinguishing them is needed later.
                dependencies.update(dev_packages)

    except toml.TomlDecodeError as e:
        print(f"Error: Could not decode Pipfile '{filepath}': {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while processing Pipfile '{filepath}': {e}")
        return {}

    # Clean up dependencies (similar to pyproject.toml handling)
    final_deps = {}
    for name, spec_info in dependencies.items():
        # Pipenv allows complex dicts like {"requests": {"version": "*", "extras": ["security"]}}
        # Or just simple strings like {"flask": "*"}
        if isinstance(spec_info, dict):
            version = spec_info.get("version", "*")
            final_deps[name] = str(version) if version is not None else "*"
        elif isinstance(spec_info, str):
            # Simple version string or "*"
            final_deps[name] = spec_info
        else:
            warnings.warn(
                f"Unexpected format for Pipfile dependency '{name}': {spec_info}. Using '*'."
            )
            final_deps[name] = "*"

    # Remove 'python' or related keys if present
    python_keys = ["python", "python_version", "python_full_version"]
    for key in python_keys:
        if key in final_deps:
            del final_deps[key]

    return final_deps


def parse_requirements_txt(filepath="requirements.txt"):
    """
    Reads dependencies from a requirements.txt file.

    Args:
        filepath (str): Path to the requirements.txt file. Defaults to "requirements.txt".

    Returns:
        dict: A dictionary of {package_name: version_specifier_string}.
              Ignores comments, empty lines, and options lines (starting with '-').
              Returns an empty dict if file not found or on parsing errors.
    """
    dependencies = {}
    if not os.path.exists(filepath):
        print(f"Info: requirements.txt not found at {filepath}")
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                # Skip empty lines, comments
                if not line or line.startswith("#"):
                    continue

                # Remove inline comments
                line = line.split("#", 1)[0].strip()
                if not line:  # Line might have been only a comment
                    continue

                # Skip options/directives (like -r, -c, -i, --hash, etc.)
                # A simple check is if it starts with '-', but allow for pkg names like '-pkg' if any exist?
                # A more robust check might involve known requirement file options
                if line.startswith("-"):
                    # Could potentially parse -e/--editable lines if needed in future
                    if line.startswith("-e") or line.startswith("--editable"):
                        warnings.warn(
                            f"Skipping editable install line in {filepath}:{line_num}: {line}"
                        )
                    else:
                        warnings.warn(
                            f"Skipping options/directive line in {filepath}:{line_num}: {line}"
                        )
                    continue

                name, spec = _parse_requirement_string(line)

                if name:
                    # Overwrite duplicates, last one wins in requirements.txt context
                    dependencies[name] = spec
                else:
                    # Warning for failed parsing is inside _parse_requirement_string
                    # Add context here if needed
                    warnings.warn(f"Could not parse requirement on line {line_num} in {filepath}")

    except FileNotFoundError:
        # This case is handled by the initial os.path.exists check,
        # but keep it for robustness in case of race conditions etc.
        print(f"Info: requirements.txt not found at {filepath}")  # Should not happen often
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while processing '{filepath}': {e}")
        return {}

    # No 'python' entry expected in requirements.txt usually, so no cleanup needed

    return dependencies


def parse_dependencies(filepath: str) -> dict[str, str]:
    """
    Detects the type of dependency file based on its name and calls the appropriate parser.

    Supports pyproject.toml, Pipfile, and requirements.txt files.

    Args:
        filepath (str): The path to the dependency file.

    Returns:
        dict: A dictionary of {package_name: version_specifier_string}.
              Returns an empty dict if the file type is not recognized or
              if the specific parser encounters an error (errors are logged
              by the individual parsers).
    """
    if not isinstance(filepath, str) or not filepath:
        warnings.warn("Invalid filepath provided.")
        return {}

    filename = os.path.basename(filepath)

    if filename == "pyproject.toml":
        return parse_pyproject_toml(filepath)
    elif filename == "Pipfile":
        return parse_pipfile(filepath)
    # Use endswith for requirements files as they can have different names (e.g., requirements-dev.txt)
    elif filename.endswith(".txt") and "requirements" in filename.lower():
        # Added check for 'requirements' in name to be slightly more specific than just any .txt
        return parse_requirements_txt(filepath)
    else:
        # Only warn if the file actually exists but is not recognized
        if os.path.exists(filepath):
            warnings.warn(
                f"Unrecognized dependency file format: {filename}. Supported formats: pyproject.toml, Pipfile, requirements*.txt"
            )
        # else: File doesn't exist, the parsers handle this internally with info messages.
        return {}
