#!/usr/bin/env bash
# Cross-language check on freshly generated logs (not just fixtures):
# Python writes real runs against fake devices, then Rust validates them and
# both folds must produce the same summary.
set -euo pipefail
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export LAB_FAKE=1 LAB_TOOLS=exp000_ir_bridge.tools:build LAB_EVENTS_DIR="$tmp"

printf 'fan.power\ny\nfireplace.power\nfireplace.power !\ny\nrobot.forward {"seconds": 0.2}\nn\nrobot.forward {"seconds": 9}\nnote crosscheck\nend\n' \
  | uv run --quiet lab session exp000-ir-bridge --run-id exp000-xcheck-r1 >/dev/null
printf 'y\nn\ny\n' | uv run --quiet lab trials exp000-ir-bridge fan.speed -n 3 --interval 0.5 --run-id exp000-xcheck-r2 --dry-run >/dev/null
uv run --quiet lab replay "$tmp/exp000-ir-bridge/exp000-xcheck-r1.jsonl" >/dev/null

cargo build --quiet --release -p labctl
./target/release/labctl stats "$tmp"
for log in "$tmp"/exp000-ir-bridge/*.jsonl; do
  uv run --quiet lab summary "$log" > "$tmp/py.json"
  ./target/release/labctl summary "$log" > "$tmp/rs.json"
  python3 - "$tmp/py.json" "$tmp/rs.json" "$log" <<'PY'
import json, sys
norm = lambda v: {k: norm(x) for k, x in v.items()} if isinstance(v, dict) else (float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
py, rs = (norm(json.load(open(p))) for p in sys.argv[1:3])
if py != rs:
    sys.exit(f"MISMATCH {sys.argv[3]}\npython: {py}\nrust:   {rs}")
print(f"same summary  {sys.argv[3].rsplit('/', 1)[-1]}")
PY
done
