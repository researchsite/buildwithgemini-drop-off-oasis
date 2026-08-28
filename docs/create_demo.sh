#!/usr/bin/env bash
set -e

echo "🌿 Running Drop-Off Oasis Demo Recording Pipeline..."
cd "$(dirname "$0")/.."

uv run python docs/capture_demo.py

echo "✅ Demo capture complete: docs/demo_walkthrough.mp4 & docs/demo_walkthrough.gif updated."
