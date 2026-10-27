# Pinned evaluation environment (open decision D10 in docs/PROJECT.md).
#
# Base: python:3.12-slim-bookworm, pinned by digest. TeX Live comes from the
# Debian bookworm apt archive, so the whole image builds reproducibly from
# one pinned layer. latexmk ships inside texlive-latex-extra. latexrun,
# Tectonic and Typst are pinned-version release artifacts, not packaged for
# Debian bookworm. auxflow itself (including bench/harness/normstate.py) is
# pip-installed into the image so every baseline script and the ground-truth
# sweep share exactly the normalisation auxflow.runtime.normalize defines --
# the "share identical normalisation" requirement in docs/EVALUATION.md.
#
# Build (from repo root): docker build -t auxflow-bench:TAG -f bench/Dockerfile .
# The resulting image ID (sha256 content digest) is the pin recorded in every
# bench/results/*.jsonl record.
# Base digest verified 2026-10-16 via `docker pull python:3.12-slim-bookworm`.
FROM python@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      texlive-latex-base \
      texlive-latex-recommended \
      texlive-latex-extra \
      texlive-bibtex-extra \
      latexmk \
      texlive-fonts-recommended \
      biber \
      poppler-utils \
      ca-certificates \
      curl \
      unzip \
      xz-utils \
    && rm -rf /var/lib/apt/lists/*

# labelschanged: loaded by the LaTeX baselines so its per-label report is
# captured, per EVALUATION.md's "Reference implementations to run alongside".
# CTAN ships it as a .dtx/.ins pair; `tex labelschanged.ins` extracts the
# .sty deterministically (verified locally against this exact zip).
RUN mkdir -p /tmp/labelschanged && cd /tmp/labelschanged \
    && curl -fsSL -o labelschanged.zip \
      https://mirrors.ctan.org/macros/latex/contrib/labelschanged.zip \
    && unzip -q labelschanged.zip && cd labelschanged \
    && tex labelschanged.ins \
    && mkdir -p /usr/share/texmf/tex/latex/labelschanged \
    && mv labelschanged.sty /usr/share/texmf/tex/latex/labelschanged/ \
    && texhash \
    && rm -rf /tmp/labelschanged

# latexrun: single-file Python 2/3 tool, pinned to one commit.
RUN curl -fsSL -o /usr/local/bin/latexrun \
      https://raw.githubusercontent.com/aclements/latexrun/38ff6ec2815654513c91f64bdf2a5760c85da26e/latexrun \
    && chmod +x /usr/local/bin/latexrun

# Tectonic 0.15.0, pinned release binary.
RUN curl -fsSL -o /tmp/tectonic.tar.gz \
      https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-gnu.tar.gz \
    && tar -xzf /tmp/tectonic.tar.gz -C /usr/local/bin \
    && rm /tmp/tectonic.tar.gz \
    && chmod +x /usr/local/bin/tectonic

# Typst 0.11.0, pinned release binary. Used only for the hand-ported
# amplifying/oscillating corpus members (b08, b11-b14), per EVALUATION.md.
RUN curl -fsSL -o /tmp/typst.tar.xz \
      https://github.com/typst/typst/releases/download/v0.11.0/typst-x86_64-unknown-linux-musl.tar.xz \
    && tar -xJf /tmp/typst.tar.xz -C /tmp \
    && mv /tmp/typst-x86_64-unknown-linux-musl/typst /usr/local/bin/typst \
    && rm -rf /tmp/typst.tar.xz /tmp/typst-x86_64-unknown-linux-musl \
    && chmod +x /usr/local/bin/typst

# Prime Tectonic's default bundle cache at build time so later invocations
# never need network access (the harness runs every container with
# --network=none for reproducibility). Covers ifthen/varioref/babel, used
# by most corpus members. biblatex is deliberately excluded: Tectonic
# bundles its own biblatex/biber pair, version-incompatible with the
# system biber installed above, so b15_ibid's Tectonic cross-check is
# expected to report that incompatibility rather than a false success.
RUN mkdir -p /tmp/tectonic-prime && cd /tmp/tectonic-prime \
    && printf '%s\n' \
      '\documentclass{article}' \
      '\usepackage{ifthen}' \
      '\usepackage{varioref}' \
      '\usepackage[ngerman]{babel}' \
      '\begin{document}' \
      'prime' \
      '\end{document}' \
      > prime.tex \
    && tectonic --outfmt pdf prime.tex \
    && cd / && rm -rf /tmp/tectonic-prime

# auxflow itself: gives every baseline script and the ground-truth sweep a
# normstate.py fixed at /opt/auxflow/bench/harness/normstate.py, and gives
# in-container drivers `import auxflow.runtime.normalize` directly.
COPY pyproject.toml README.md LICENSE /opt/auxflow/
COPY src /opt/auxflow/src
COPY bench/harness /opt/auxflow/bench/harness
COPY bench/baselines /opt/auxflow/bench/baselines
RUN SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0+bench pip install --no-cache-dir /opt/auxflow

RUN pdflatex --version | head -1 \
    && latexmk --version | head -1 \
    && bibtex --version | head -1 \
    && biber --version \
    && pdftotext -v 2>&1 | head -1 \
    && latexrun --help > /dev/null \
    && tectonic --version \
    && typst --version \
    && kpsewhich labelschanged.sty \
    && python3 -c "import auxflow; from auxflow.runtime.normalize import normalize_state"

WORKDIR /work
