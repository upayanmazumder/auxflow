#!/usr/bin/env bash
# Render every Mermaid source in docs/figures/src/*.mmd to docs/figures/<name>.png.
#
# The Review 2 and Review 3 documents place these PNGs at 15.5 cm width on A4.
# Renders use a white background and scale 3 so the text stays sharp in print.
#
# Run from any directory (optional names render only those sources):
#     bash scripts/render_figures.sh [architecture arg-b08 ...]
#
# Requires Node.js (npx) and a Chrome or Chromium binary. Set CHROME to override
# the default browser path.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/docs/figures/src"
OUT="$ROOT/docs/figures"
CHROME="${CHROME:-/usr/bin/google-chrome-stable}"
MMDC_VERSION="${MMDC_VERSION:-11}"

if [[ ! -x "$CHROME" ]]; then
    echo "error: Chrome not found at $CHROME (set CHROME)" >&2
    exit 1
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

cat >"$work/puppeteer.json" <<JSON
{"executablePath": "$CHROME", "args": ["--no-sandbox", "--disable-gpu"]}
JSON

cat >"$work/mermaid.json" <<'JSON'
{
  "theme": "base",
  "themeVariables": {
    "fontFamily": "DejaVu Sans, Arial, sans-serif",
    "fontSize": "16px",
    "primaryColor": "#DCE8F3",
    "primaryBorderColor": "#0D1B2A",
    "primaryTextColor": "#0D1B2A",
    "lineColor": "#33415C",
    "clusterBkg": "#F7F9FC",
    "clusterBorder": "#8A99AD",
    "edgeLabelBackground": "#FFFFFF",
    "actorBkg": "#DCE8F3",
    "actorBorder": "#0D1B2A",
    "noteBkgColor": "#FFF3CF",
    "noteBorderColor": "#B58900"
  },
  "flowchart": {"htmlLabels": true, "curve": "basis", "padding": 12, "wrappingWidth": 260},
  "sequence": {"mirrorActors": false, "wrap": true, "width": 170, "messageFontSize": 15, "noteFontSize": 14, "actorFontSize": 15}
}
JSON

shopt -s nullglob
if (( $# > 0 )); then
    sources=()
    for name in "$@"; do
        sources+=("$SRC/$name.mmd")
    done
else
    sources=("$SRC"/*.mmd)
fi
if (( ${#sources[@]} == 0 )); then
    echo "error: no Mermaid sources in $SRC" >&2
    exit 1
fi

for source in "${sources[@]}"; do
    name="$(basename "$source" .mmd)"
    echo "rendering $name.png"
    PUPPETEER_SKIP_DOWNLOAD=1 npx -y "@mermaid-js/mermaid-cli@$MMDC_VERSION" \
        --quiet \
        --input "$source" \
        --output "$OUT/$name.png" \
        --configFile "$work/mermaid.json" \
        --puppeteerConfigFile "$work/puppeteer.json" \
        --backgroundColor white \
        --scale 3 \
        --width 1100
done
