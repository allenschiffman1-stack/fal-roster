#!/usr/bin/env bash
# Generate 12 placeholder mp4s. For characters with an existing backdrop png in
# assets/video/, loop the png as a static 3-second h264 mp4. For the rest, use
# the portrait from assets/characters/ scaled into a 1280x720 frame on a dark bg.

set -euo pipefail
cd "$(dirname "$0")/../.."

CHARACTERS=(master-chief kratos link mario samus cloud snake geralt aloy lara arthur joel)

for name in "${CHARACTERS[@]}"; do
  src_bg="assets/video/${name}.png"
  src_portrait="assets/characters/${name}.png"
  out="assets/video/${name}.mp4"

  if [ -f "$src_bg" ]; then
    src="$src_bg"
    filter="scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,format=yuv420p"
  else
    src="$src_portrait"
    # Portrait on dark cyberpunk bg, centered.
    filter="scale=720:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0a0e1a,format=yuv420p"
  fi

  ffmpeg -y -loglevel error -loop 1 -t 3 -i "$src" \
    -vf "$filter" -c:v libx264 -preset fast -crf 28 -movflags +faststart \
    -an "$out"

  printf '%-15s -> %s (%s)\n' "$name" "$out" "$(stat -c %s "$out" 2>/dev/null || stat -f %z "$out")"
done
