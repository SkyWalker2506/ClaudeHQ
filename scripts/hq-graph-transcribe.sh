#!/usr/bin/env bash
# hq-graph-transcribe.sh — Transcribe audio/video with faster-whisper.
# Usage: hq graph transcribe <file> [--model base|small|medium]
set -euo pipefail

RED=$'\033[0;31m'; GREEN=$'\033[0;32m'; YELLOW=$'\033[1;33m'; GRAY=$'\033[0;90m'; NC=$'\033[0m'

file="${1:-}"
shift || true
model="base"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) model="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[[ -z "$file" ]] && { echo "${RED}error:${NC} input file required"; exit 1; }
[[ -f "$file" ]] || { echo "${RED}error:${NC} file not found: $file"; exit 1; }

if ! python3 -c "import faster_whisper" 2>/dev/null; then
  echo "${YELLOW}faster-whisper not installed.${NC}"
  echo "Install with: ${GRAY}pip install --user faster-whisper${NC}"
  read -p "Install now? [y/N] " yn
  case "$yn" in
    y|Y) python3 -m pip install --user faster-whisper || { echo "${RED}install failed${NC}"; exit 1; } ;;
    *)   echo "aborted"; exit 1 ;;
  esac
fi

out="${file}.transcript.txt"
echo "${GRAY}Transcribing (model=$model) → $out${NC}"

python3 - "$file" "$out" "$model" <<'PY'
import sys
from faster_whisper import WhisperModel
inp, outp, model_name = sys.argv[1], sys.argv[2], sys.argv[3]
model = WhisperModel(model_name, device="cpu", compute_type="int8")
segments, info = model.transcribe(inp, beam_size=5, language=None, vad_filter=True)
print(f"detected language: {info.language} (prob={info.language_probability:.2f})")
with open(outp, "w") as f:
    for seg in segments:
        line = f"[{seg.start:6.1f} → {seg.end:6.1f}] {seg.text.strip()}"
        f.write(line + "\n")
        print(line)
print(f"\n✓ written: {outp}")
PY

echo "${GREEN}✓ transcript written${NC}"
