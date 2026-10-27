---
title: "Review 2"
parent: "Reviews"
nav_order: 2
---

{: .note }
**Downloads:** [Document (PDF)](/reviews/downloads/review2-document.pdf) · [Document (DOCX)](/reviews/downloads/review2-document.docx) · [Slides (PDF)](https://github.com/upayanmazumder/auxflow/raw/main/presentation/review2-auxflow.pdf)

# AuxFlow: Review 2 Viva Preparation

Static Analysis for Multi-Pass Document Compilation · Upayan Mazumder (24BDS0367) · Compiler Design Lab

Companion guide for Review 2: Front-End, Semantic Analysis, and Intermediate Representation (Phases 1 to 7).
All 16 implementation phases are complete. Tests: 245 pass, 1 skipped. mypy --strict is clean on 41 files. ruff lint is clean on src, tests, and bench. This review presents Phases 1 to 7.
Formal assessment document: `docs/review2-document.docx` and `docs/review2-document.pdf`.
Framing remains conservative: AuxFlow is a compiler-based static analysis of dependency structure in multi-pass compilation.

---

### 1. What does the lexer do differently from standard compilers?
- Implements the 16 TeX category codes (catcodes) via a table-driven scanner in `auxflow.lexer`.
- Catcodes define lexical interpretation dynamically per character class.
- Recognizes comments (`%` vs `\%`) and inline verbatim blocks (`\verb|...|`) without expansion.
- Verifies full round-trip preservation from source characters to tokens.

### 2. How does the parser handle LaTeX without a full TeX engine?
- Hand-written recursive descent with one token of lookahead (`auxflow.parser.recursive`).
- Operates strictly over a **declared language subset**; unsupported tokens map to `Opaque` nodes.
- Uses an argument signature table (`auxflow.parser.signatures`) to assign mandatory and optional groups.
- Employs fault-tolerant error recovery: malformed input never raises exceptions and always produces an AST.

### 3. How are multi-file documents structured and analyzed?
- The parser builds an AST per file and records file inclusions (`\input` and `\include`).
- `auxflow.ast.forest` links file ASTs into a multi-file dependency forest.
- DFS coloring detects recursive inclusion cycles and isolates unreachable files.

### 4. What symbol tables exist, and why use two-pass resolution?
- Six symbol tables: `LabelTable`, `RefTable`, `CiteTable`, `PackageTable`, `FileTable`, `CounterTable`.
- First pass (`declare`): records all definitions across all files without binding uses.
- Second pass (`resolve`): binds `\ref`, `\pageref`, and `\cite` uses across file boundaries.
- Two-pass traversal prevents forward references across files from reporting as undefined.

### 5. What semantic checks run before compilation?
- `auxflow check` verifies semantic consistency with zero engine executions.
- Detects undefined references, missing citations, duplicate labels, unresolvable file includes, and missing graphics.
- Warns on unmodelled packages via `PackageTable` before building the graph.

### 6. What is the Auxiliary Reference Graph (ARG)?
- The compiler's Intermediate Representation (IR), implemented in `auxflow.ir`.
- Nodes represent instance-level auxiliary facts (`LABEL_NUMBER`, `LABEL_PAGE`, `PAGEREF_USE`, `TOC_ENTRY`, `BBL`).
- Edges represent lagged data dependencies (`AUX_ROUNDTRIP`, `TOOL`, `LAYOUT`, `STRUCTURAL`) with pass lags.
- Every node and edge carries a mandatory source span for diagnostic traceability.

### 7. What is the `exists` / `value` split in the IR?
- List entries (`\contentsline`) split into two distinct facts:
  1. `exists`: presence of the entry, determined by structure, feeding `CONTENT_VOLUME`.
  2. `value`: typeset page number of the entry.
- Decouples pagination shift from reference consumption, preventing ordinary tables of contents from forming false cycles.

### 8. How can we inspect the compiler pipeline at Review 2?
- Lexer: `auxflow tokens FILE`
- AST: `auxflow ast FILE`
- Symbol tables: `auxflow symbols FILE`
- Semantic analysis: `auxflow check FILE`
- Intermediate representation: `auxflow graph FILE` (exports Graphviz DOT format)

---

## Quick Backups (Viva Questions)
- **Why not use Flex/Bison?** TeX catcodes make grammar context-sensitive; hand-written lookahead handles delimiter-driven verbatim and macro arguments reliably.
- **How are spans preserved?** Every AST node is a frozen dataclass with a mandatory `Span(file_id, start, end)`.
- **Does semantic check execute TeX?** No. It performs pure static symbol table lookup in linear time.
- **What is the complexity of IR lowering?** $O(V + E)$ single-pass traversal over the resolved AST forest.
