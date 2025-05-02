#!/bin/bash

# Get version from __init__.py
VERSION=$(grep -E '__version__[[:space:]]*=[[:space:]]*"[^"]+"' src/omegacloud_cli/__init__.py | sed -E 's/.*"([^"]+)".*/\1/')

# Update pyproject.toml version (macOS compatible sed)
sed -i '' "s/^version = .*/version = \"$VERSION\"/" pyproject.toml

rm -rf dist/
# uv pip freeze > requirements.txt
uv export --no-dev --no-hashes > requirements.txt
pip install -e .
python -m build
twine upload dist/*

