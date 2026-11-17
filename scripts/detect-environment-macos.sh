#!/bin/bash

set -u

photoshop_path=""
as_json=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --photoshop-path)
            shift
            photoshop_path="${1:-}"
            ;;
        --json)
            as_json=1
            ;;
        -h|--help)
            echo "Usage: bash scripts/detect-environment-macos.sh [--photoshop-path /Applications/Adobe\ Photoshop.app] [--json]"
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
    echo "This detector supports macOS only." >&2
    exit 4
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
skill_root="$(cd "$script_dir/.." && pwd)"
font_dir="$skill_root/assets/fonts"
manifest_path="$font_dir/font-manifest.json"
candidate_file="$(mktemp -t font-image-text-replace-photoshop.XXXXXX)"
trap 'rm -f "$candidate_file"' EXIT

json_escape() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

plist_value() {
    key="$1"
    plist="$2"
    if [ -x /usr/libexec/PlistBuddy ]; then
        /usr/libexec/PlistBuddy -c "Print :$key" "$plist" 2>/dev/null || true
    else
        defaults read "${plist%.plist}" "$key" 2>/dev/null || true
    fi
}

add_candidate() {
    app_path="$1"
    source="$2"
    priority="$3"

    [ -n "$app_path" ] || return 0
    [ -d "$app_path" ] || return 0
    case "$app_path" in
        *.app) ;;
        *) return 0 ;;
    esac

    app_path="$(cd "$(dirname "$app_path")" && pwd)/$(basename "$app_path")"
    plist="$app_path/Contents/Info.plist"
    [ -f "$plist" ] || return 0

    version="$(plist_value CFBundleShortVersionString "$plist")"
    executable_name="$(plist_value CFBundleExecutable "$plist")"
    bundle_id="$(plist_value CFBundleIdentifier "$plist")"
    [ -n "$executable_name" ] || executable_name="$(basename "$app_path" .app)"
    executable_path="$app_path/Contents/MacOS/$executable_name"
    [ -x "$executable_path" ] || return 0

    major="$(printf '%s' "$version" | sed -E 's/^([0-9]+).*/\1/')"
    case "$major" in
        ''|*[!0-9]*) major=0 ;;
    esac

    printf '%s|%s|%s|%s|%s|%s|%s\n' \
        "$priority" "$major" "$version" "$app_path" "$executable_path" "$bundle_id" "$source" >> "$candidate_file"
}

add_candidate "$photoshop_path" "parameter" 1000
add_candidate "${PHOTOSHOP_APP:-}" "PHOTOSHOP_APP" 900

for app_path in /Applications/Adobe\ Photoshop*.app "$HOME"/Applications/Adobe\ Photoshop*.app; do
    [ -e "$app_path" ] || continue
    add_candidate "$app_path" "applications-directory" 500
done

selected=""
if [ -s "$candidate_file" ]; then
    selected="$(sort -t '|' -k1,1nr -k2,2nr "$candidate_file" | head -n 1)"
fi

font_expected=0
font_present=0
if [ -f "$manifest_path" ]; then
    font_expected="$(grep -c '"file"[[:space:]]*:' "$manifest_path" | tr -d ' ')"
fi
if [ -d "$font_dir" ]; then
    font_present="$(find "$font_dir" -maxdepth 1 -type f \( -iname '*.ttf' -o -iname '*.otf' -o -iname '*.ttc' \) | wc -l | tr -d ' ')"
fi

os_version="$(sw_vers -productVersion 2>/dev/null || true)"
arch="$(uname -m)"

found=false
selected_json="null"
guidance=""
if [ -n "$selected" ]; then
    found=true
    IFS='|' read -r priority major version app_path executable_path bundle_id source <<EOF
$selected
EOF
    profile="unknown-version-smoke-test-required"
    if [ "$major" -ge 22 ] 2>/dev/null; then
        profile="standard-jsx"
    elif [ "$major" -gt 0 ] 2>/dev/null; then
        profile="legacy-jsx-smoke-test-required"
    fi
    selected_json="{\"app_path\":\"$(json_escape "$app_path")\",\"executable_path\":\"$(json_escape "$executable_path")\",\"bundle_id\":\"$(json_escape "$bundle_id")\",\"product_version\":\"$(json_escape "$version")\",\"major_version\":$major,\"source\":\"$(json_escape "$source")\",\"compatibility_profile\":\"$profile\"}"
else
    guidance="Adobe Photoshop was not detected. Install Photoshop through Adobe Creative Cloud, launch it once, and rerun this check. For a custom location, pass --photoshop-path or set PHOTOSHOP_APP. Native editable-text PSD delivery is blocked until Photoshop is available."
fi

fonts_complete=false
if [ "$font_expected" -gt 0 ] && [ "$font_expected" -eq "$font_present" ]; then
    fonts_complete=true
fi

if [ "$as_json" -eq 1 ]; then
    printf '{\n'
    printf '  "schema_version": 1,\n'
    printf '  "platform": {"os": "macOS", "version": "%s", "architecture": "%s"},\n' "$(json_escape "$os_version")" "$(json_escape "$arch")"
    printf '  "photoshop": {"found": %s, "selected": %s, "guidance": "%s"},\n' "$found" "$selected_json" "$(json_escape "$guidance")"
    printf '  "bundled_fonts": {"manifest": "%s", "expected": %s, "present": %s, "complete": %s}\n' "$(json_escape "$manifest_path")" "$font_expected" "$font_present" "$fonts_complete"
    printf '}\n'
else
    echo "macOS: $os_version ($arch)"
    if [ "$found" = true ]; then
        echo "Photoshop: $app_path"
        echo "Version: $version"
        echo "Profile: $profile"
    else
        echo "Photoshop: not found"
        echo "$guidance"
    fi
    echo "Bundled fonts: $font_present/$font_expected"
fi

if [ "$found" != true ]; then
    exit 2
fi
if [ "$fonts_complete" != true ]; then
    exit 3
fi
exit 0
