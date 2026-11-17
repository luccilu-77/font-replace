#!/bin/bash

set -u

photoshop_path=""
timeout_seconds=120

while [ "$#" -gt 0 ]; do
    case "$1" in
        --photoshop-path)
            shift
            photoshop_path="${1:-}"
            ;;
        --timeout)
            shift
            timeout_seconds="${1:-120}"
            ;;
        -h|--help)
            echo "Usage: bash scripts/run-photoshop-smoke-test-macos.sh [--photoshop-path /Applications/Adobe\ Photoshop.app] [--timeout 120]"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 64
            ;;
    esac
    shift
done

if [ "$(uname -s)" != "Darwin" ]; then
    echo "This runner supports macOS only." >&2
    exit 4
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
jsx_path="$script_dir/photoshop-smoke-test.jsx"
[ -f "$jsx_path" ] || { echo "Smoke-test JSX not found: $jsx_path" >&2; exit 6; }

if [ -z "$photoshop_path" ]; then
    photoshop_path="${PHOTOSHOP_APP:-}"
fi
if [ -z "$photoshop_path" ]; then
    for candidate in /Applications/Adobe\ Photoshop*.app "$HOME"/Applications/Adobe\ Photoshop*.app; do
        [ -d "$candidate" ] || continue
        photoshop_path="$candidate"
    done
fi
[ -d "$photoshop_path" ] || { echo "Photoshop app not found. Use --photoshop-path or PHOTOSHOP_APP." >&2; exit 2; }

app_name="$(basename "$photoshop_path" .app)"
temp_root="${TMPDIR:-/tmp}"
result_path="${temp_root%/}/font-image-text-replace-photoshop-smoke.json"
rm -f "$result_path"

osascript <<EOF
tell application "$app_name"
    activate
    do javascript file (POSIX file "$jsx_path")
end tell
EOF
status=$?

if [ "$status" -ne 0 ]; then
    echo "Photoshop automation failed. Allow automation access in System Settings > Privacy & Security > Automation, then retry." >&2
    exit "$status"
fi

elapsed=0
while [ "$elapsed" -lt "$timeout_seconds" ]; do
    if [ -f "$result_path" ]; then
        cat "$result_path"
        exit 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

echo "Timed out waiting for Photoshop smoke-test output: $result_path" >&2
exit 3
