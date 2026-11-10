#!/bin/bash
# Legacy alias: redirect to lockin_mode.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/lockin_mode.sh" "$@"
