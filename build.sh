#!/usr/bin/env bash
# Builds GPT knowledge from the canonical skill and runs the test suite.
# Run after editing anything under claude/fitcoach-pro/.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
en="$root/claude/fitcoach-pro"

# 1. GPT knowledge — references, templates, and the tools a Code Interpreter can run
build_gpt() {
  local src="$1" dest="$2" label="$3"
  rm -rf "$dest"; mkdir -p "$dest"
  cp "$src"/references/*.md "$dest/"
  cp "$src"/assets/*.md "$dest/"
  cp "$src"/tools/*.py "$dest/"
  cp "$src"/data/exercises.json "$dest/"
  rm -f "$dest/__init__.py"
  # dashboard.py, sheet.py and cohort.py stay out: the GPT Builder caps
  # knowledge at 20 files, and all three walk the local filesystem — work the
  # machine holding the client folders does, not a chat sandbox. INDEX.md is a Claude-only router.
  rm -f "$dest/dashboard.py" "$dest/sheet.py" "$dest/cohort.py" "$dest/INDEX.md"
  local n; n=$(ls -1 "$dest" | wc -l)
  echo "$label: $n files"
  [ "$n" -le 20 ] || echo "WARNING: the GPT Builder accepts at most 20 knowledge files — trim before uploading."
}

build_gpt "$en" "$root/gpt/knowledge" "gpt/knowledge"

# 2. the tests must pass, or the numbers cannot be trusted
echo
( cd "$en" && python3 -m unittest discover -s tools/tests -t tools -q ) && echo "tests: OK"
