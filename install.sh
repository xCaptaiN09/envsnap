#!/usr/bin/env bash
set -e
# envsnap easy installer: pipx > pip fallback
if command -v pipx >/dev/null 2>&1; then
  pipx install envsnap
elif command -v pip >/dev/null 2>&1; then
  pip install envsnap
else
  echo "need pip or pipx (python 3.10+)"
  exit 1
fi
envsnap --help
