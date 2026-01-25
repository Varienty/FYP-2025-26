#!/bin/bash
set -euo pipefail

echo "[prebuild] Installing OpenCV runtime dependencies..."
dnf install -y libX11 libXext libSM libICE libXrender libxcb mesa-libGL >/var/log/eb-opencv-deps.log 2>&1 || {
  echo "[prebuild] Failed to install OpenCV deps" >&2
  exit 1
}
