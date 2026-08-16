#!/usr/bin/env bash
# ship.sh — one-shot ship loop for the gosura landing:
#   assemble fragments -> validate -> save a DRAFT version over MCP -> QA the server render.
#
# Usage:
#   tools/ship.sh [-l "label"] [-n] [token-or-mcp-url]
#
#   -l "label"   version label (default: "ship <date>")
#   -n           dry-run: assemble + validate, then show the save call without any network write
#   argument     either the bare token or the full https://olive.kz/mcp/landings/<token> URL;
#                if omitted, $OLIVE_MCP_URL must already be exported
#
# Safety by construction:
#   * saves are always --status draft — visitors never see them; the version list only grows;
#   * this script NEVER calls activate. Going live stays a deliberate human command:
#       ./tools/olive.py activate <id>        (rollback = activate the previous id)
#   * the token is a credential: it is never echoed here, never written to disk, and must
#     never be committed. olive.py masks it in its own error output.
set -euo pipefail
cd "$(dirname "$0")/.."

label="ship $(date +%F)"
dry=0
while getopts "l:n" opt; do
  case "$opt" in
    l) label=$OPTARG ;;
    n) dry=1 ;;
    *) echo "usage: tools/ship.sh [-l label] [-n] [token-or-mcp-url]" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))

arg="${1:-}"
if [ -n "$arg" ]; then
  case "$arg" in
    https://*) export OLIVE_MCP_URL="$arg" ;;
    *)         export OLIVE_MCP_URL="https://olive.kz/mcp/landings/$arg" ;;
  esac
fi
: "${OLIVE_MCP_URL:?export OLIVE_MCP_URL or pass the token as an argument}"

echo "== assemble =="
python3 tools/assemble.py

echo "== validate =="
python3 tools/validate.py landing/config.json   # non-zero exit aborts the ship (set -e)

if [ "$dry" -eq 1 ]; then
  echo "== save (dry-run) =="
  ./tools/olive.py save gosura landing/config.json --label "$label" --status draft --dry-run
  echo "dry-run: nothing was saved"
  exit 0
fi

echo "== save draft =="
out=$(./tools/olive.py save gosura landing/config.json --label "$label" --status draft)
printf '%s\n' "$out"
vid=$(printf '%s' "$out" | python3 -c 'import sys,json; print(json.load(sys.stdin)["version"]["id"])')

echo "== qa (server render of $vid) =="
qa_status=0
python3 tools/qa.py "$vid" || qa_status=$?

echo
echo "draft $vid saved — preview: https://olive.kz/l/gosura?v=$vid"
if [ "$qa_status" -ne 0 ]; then
  echo "QA FAILED — do not activate this version; fix and re-ship." >&2
  exit "$qa_status"
fi
echo "QA passed. Activation is manual and deliberate: ./tools/olive.py activate $vid"
