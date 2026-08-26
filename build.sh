#!/usr/bin/env bash
# Regenerates everything derived from the canonical English skill:
#   - the Python tools and exercise catalog inside the pt-BR skill
#   - the GPT knowledge folders for both languages
# Run after editing anything under claude/fitcoach-pro/. Otherwise the copies
# drift apart in silence, which is the failure mode this script exists to stop.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
en="$root/claude/fitcoach-pro"
pt="$root/claude/fitcoach-pro-pt-BR"

# 1. tools + data are code: one source, copied into the translated skill
rm -rf "$pt/tools" "$pt/data"
cp -r "$en/tools" "$pt/tools"
cp -r "$en/data" "$pt/data"
find "$pt/tools" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
echo "pt-BR skill: tools and data synced from the English source"

# 2. GPT knowledge — references, templates, and the tools a Code Interpreter can run
build_gpt() {
  local src="$1" dest="$2" label="$3"
  rm -rf "$dest"; mkdir -p "$dest"
  cp "$src"/references/*.md "$dest/"
  cp "$src"/assets/*.md "$dest/"
  cp "$src"/tools/*.py "$dest/"
  cp "$src"/data/exercises.json "$dest/"
  rm -f "$dest/__init__.py"
  # dashboard.py and sheet.py stay out: the GPT Builder caps knowledge at 20
  # files, and both operate on local HTML — work better done on the machine
  # that holds the files.
  rm -f "$dest/dashboard.py" "$dest/sheet.py"
  local n; n=$(ls -1 "$dest" | wc -l)
  echo "$label: $n files"
  [ "$n" -le 20 ] || echo "WARNING: the GPT Builder accepts at most 20 knowledge files — trim before uploading."
}

build_gpt "$en" "$root/gpt/knowledge"       "gpt/knowledge (en)"
build_gpt "$pt" "$root/gpt/pt-BR/knowledge" "gpt/pt-BR/knowledge"

# 3. the tests must pass, or the numbers cannot be trusted — and they must pass
#    from either copy, since a trainer who installs only the translated skill
#    should be able to verify their install
echo
( cd "$en" && python3 -m unittest discover -s tools/tests -t tools -q ) && echo "tests (en): OK"
( cd "$pt" && python3 -m unittest discover -s tools/tests -t tools -q ) && echo "tests (pt-BR): OK"
