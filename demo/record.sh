#!/usr/bin/env bash
# Rebuild assets/doccanon-demo.gif from the paced DocCanon walkthrough.
#
# Pipeline:
#   1. demo/prepare.py builds a governed project where covered code later drifts
#      away from its canonical owner (the same shape as scripts/demo.py).
#   2. demo/demo.tape records a paced terminal walkthrough to MP4 (VHS).
#   3. This script encodes that MP4 into the looping GIF used by the README.
#
# VHS 0.12.0 has a regression that cancels the ffmpeg context before encoding
# and silently writes no file; this script uses VHS 0.11.0 (downloaded into
# demo/.tools/ if needed). Override with: VHS=/path/to/vhs demo/record.sh

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/.." && pwd)"
version="0.11.0"
tools="$here/.tools"
build="$here/.build"
demo_path="${DEMO_PATH:-/tmp/doccanon-demo}"
recording="$build/doccanon-demo.mp4"

# Resolve a working VHS binary.
if [[ -n "${VHS:-}" ]]; then
  bin="$VHS"
elif command -v vhs >/dev/null 2>&1 && ! vhs --version 2>/dev/null | grep -q '0\.12\.0'; then
  bin="$(command -v vhs)"
elif [[ -x "$tools/vhs" ]]; then
  bin="$tools/vhs"
else
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) asset="Darwin_arm64" ;;
    Darwin-x86_64) asset="Darwin_x86_64" ;;
    Linux-aarch64 | Linux-arm64) asset="Linux_arm64" ;;
    Linux-x86_64) asset="Linux_x86_64" ;;
    *)
      echo "No pinned VHS build for $(uname -s)-$(uname -m); set VHS=/path/to/vhs" >&2
      exit 1
      ;;
  esac
  echo "Downloading VHS v${version} (${asset}) into demo/.tools/..." >&2
  mkdir -p "$tools"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  url="https://github.com/charmbracelet/vhs/releases/download/v${version}/vhs_${version}_${asset}.tar.gz"
  curl -fsSL "$url" -o "$tmp/vhs.tar.gz"
  tar -xzf "$tmp/vhs.tar.gz" -C "$tmp"
  cp "$tmp/vhs_${version}_${asset}/vhs" "$tools/vhs"
  chmod +x "$tools/vhs"
  bin="$tools/vhs"
fi

mkdir -p "$build" "$root/assets"
python3 "$here/prepare.py" --path "$demo_path"

# The tape is a template so the demo project path stays configurable.
sed -e "s#__DEMO_PATH__#${demo_path}#g" -e "s#__REPO__#${root}#g" \
  "$here/demo.tape" > "$build/demo.tape"

cd "$root"
"$bin" "$build/demo.tape"

ffmpeg -v error -y -i "$recording" -filter_complex \
  "[0:v]fps=15,scale=1200:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=192:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
  -loop 0 "$root/assets/doccanon-demo.gif"

echo "Wrote $root/assets/doccanon-demo.gif" >&2
