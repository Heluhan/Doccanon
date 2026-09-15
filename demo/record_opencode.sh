#!/usr/bin/env bash
# Rebuild assets/doccanon-demo.gif from a real opencode session.
#
# Pipeline:
#   1. demo/opencode-demo.tape records a real opencode session to MP4 (VHS).
#   2. This script trims/speeds that recording and encodes the looping GIF.
#
# VHS 0.12.0 has a regression that cancels the ffmpeg context before encoding
# and silently writes no file; this script uses VHS 0.11.0 (downloaded into
# demo/.tools/ if needed). Override with: VHS=/path/to/vhs demo/record_opencode.sh
#
# Session timing varies between runs, so the trim window can be tuned:
#   START=7 END=30.5 SPEED=1.5 demo/record_opencode.sh

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/.." && pwd)"
version="0.11.0"
tools="$here/.tools"
build="$here/.build"
session="$build/opencode-session.mp4"

start="${START:-7}"
end="${END:-30.5}"
speed="${SPEED:-1.5}"

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

mkdir -p "$build"
cd "$root"
"$bin" demo/opencode-demo.tape

mkdir -p "$root/assets"
ffmpeg -v error -y -i "$session" -filter_complex \
  "[0:v]trim=start=${start}:end=${end},setpts=(PTS-STARTPTS)/${speed},fps=16,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=192:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
  -loop 0 "$root/assets/doccanon-demo.gif"

echo "Wrote $root/assets/doccanon-demo.gif" >&2
