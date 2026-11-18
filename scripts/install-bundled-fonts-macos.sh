#!/bin/bash

set -u

confirmed=0
force=0
dry_run=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --confirm-authorized-use)
            confirmed=1
            ;;
        --force)
            force=1
            ;;
        --dry-run)
            dry_run=1
            ;;
        -h|--help)
            echo "Usage: bash scripts/install-bundled-fonts-macos.sh [--dry-run] [--confirm-authorized-use] [--force]"
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
    echo "This installer supports macOS only." >&2
    exit 4
fi

if [ "$dry_run" -ne 1 ] && [ "$confirmed" -ne 1 ]; then
    echo "Installation requires explicit authorization." >&2
    echo "Confirm licensed use, then rerun with --confirm-authorized-use." >&2
    exit 5
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
skill_root="$(cd "$script_dir/.." && pwd)"
font_dir="$skill_root/assets/fonts"
destination="$HOME/Library/Fonts"

if [ ! -d "$font_dir" ]; then
    echo "Bundled font directory not found: $font_dir" >&2
    exit 6
fi

installed=0
skipped=0
failed=0
expected=0

if [ "$dry_run" -ne 1 ]; then
    mkdir -p "$destination" || exit 7
fi

for source in "$font_dir"/*.ttf "$font_dir"/*.otf "$font_dir"/*.ttc; do
    [ -f "$source" ] || continue
    expected=$((expected + 1))
    name="$(basename "$source")"
    target="$destination/$name"

    if [ -f "$target" ] && [ "$force" -ne 1 ]; then
        echo "SKIP  $name"
        skipped=$((skipped + 1))
        continue
    fi

    if [ "$dry_run" -eq 1 ]; then
        echo "WOULD_INSTALL  $name -> $target"
        continue
    fi

    if cp -f "$source" "$target"; then
        chmod 644 "$target" 2>/dev/null || true
        echo "INSTALLED  $name"
        installed=$((installed + 1))
    else
        echo "FAILED  $name" >&2
        failed=$((failed + 1))
    fi
done

echo "SUMMARY expected=$expected installed=$installed skipped=$skipped failed=$failed destination=$destination"
if [ "$dry_run" -eq 1 ]; then
    echo "DRY_RUN no files were changed"
else
    echo "NEXT_STEP quit and reopen Photoshop, then verify the actual font name with a test text layer"
fi

if [ "$failed" -gt 0 ]; then
    exit 1
fi
exit 0
