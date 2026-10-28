#!/usr/bin/env bash
# Render every Mermaid source in paper/figures/src/*.mmd to a vector PDF in paper/figures/.
#
# Run from any directory (optional names render only those sources):
#     bash paper/render_figures.sh [pipeline arg-model ...]
#
# Requires Node.js (npx) and a Chrome or Chromium binary. Set CHROME to override
# the default browser path. The theme matches scripts/render_figures.sh.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/figures/src"
OUT="$HERE/figures"
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
    "fontSize": "18px",
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
  "flowchart": {"htmlLabels": true, "curve": "basis", "padding": 10, "wrappingWidth": 260},
  "sequence": {"mirrorActors": false, "wrap": true, "width": 190, "messageFontSize": 17, "noteFontSize": 16, "actorFontSize": 17},
  "er": {"fontSize": 24, "useMaxWidth": false, "entityPadding": 10, "minEntityWidth": 90, "minEntityHeight": 50}
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
    echo "rendering $name.pdf"
    PUPPETEER_SKIP_DOWNLOAD=1 npx -y "@mermaid-js/mermaid-cli@$MMDC_VERSION" \
        --quiet \
        --input "$source" \
        --output "$OUT/$name.pdf" \
        --configFile "$work/mermaid.json" \
        --puppeteerConfigFile "$work/puppeteer.json" \
        --backgroundColor white \
        --pdfFit \
        --width 1000
done
