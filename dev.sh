#!/bin/bash
# Beginner-friendly wrapper for the development helper script.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/scripts/dev.sh" "$@"
