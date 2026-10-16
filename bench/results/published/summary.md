## Mechanism-coverage table

| Document | Mechanism | Expected | Observed (D) | Declared? | Match |
|---|---|---|---|---|---|
| `b01_plain` | Plain prose with no auxiliary-state producers or consumers | CERTIFIED | CERTIFIED | no | yes |
| `b02_backref` | A label precedes the reference that reads its section number | CERTIFIED | CERTIFIED | no | yes |
| `b03_fwdref` | A reference precedes the label that supplies its section number | CERTIFIED | CERTIFIED | no | yes |
| `b04_chain` | Contents extent shifts pagination before a page reference reads the closing label | CERTIFIED | CERTIFIED | no | yes |
| `b05_toc` | Generated contents entries alter the list extent without any reference use | CERTIFIED | CERTIFIED | no | yes |
| `b06_bib` | Citation and bibliography add a tool edge before a generated-list pagination chain | CERTIFIED | CERTIFIED | no | yes |
| `b07_footnote` | M7 footnote placement feedback through the typeset width of a resolved page reference | UNKNOWN | UNKNOWN | no | yes |
| `b08_cycle` | M1: a page reference bounds a loop that emits pages before its own target label | AMPLIFYING | AMPLIFYING | no | yes |
| `b09_thesis` | Realistic multi-chapter document: three interacting generated lists, bibliography, cross-chapter references, an unreachable chapter file, and an active-character caption | CERTIFIED | CERTIFIED | no | yes |
| `b10_random` | M8: a pdfTeX random draw changes a generated auxiliary record without a reference dependency | UNKNOWN | UNKNOWN | no | yes |
| `b11_width` | M3 resolved page-number width changes a line break and page placement | CERTIFIED | CERTIFIED | yes | yes (declared) |
| `b12_float` | M4 top float placement and Roman page number width can oscillate | CERTIFIED | CERTIFIED | yes | yes (declared) |
| `b13_varioref` | M6 varioref changes reference text according to relative float placement | CERTIFIED | CERTIFIED | yes | yes (declared) |
| `b14_ifthen` | M2 ifthenelse selects a large or small A according to the label's previous page | AMPLIFYING | AMPLIFYING | no | yes |
| `b15_ibid` | M5 a citation style selects a shorter form when the prior citation is on the same page | UNKNOWN | UNKNOWN | no | yes |

## Oracle-comparison table (executions to certify)

| Document | N* | A | B | C | C' | C'' | D | E |
|---|---|---|---|---|---|---|---|---|
| `b01_plain` | 1 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 1.0, p95 1.0, IQR [1.0, 1.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] |
| `b02_backref` | 2 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] |
| `b03_fwdref` | 2 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] |
| `b04_chain` | 2 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] |
| `b05_toc` | 3 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 1.0, p95 1.0, IQR [1.0, 1.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] |
| `b06_bib` | 3 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] |
| `b07_footnote` | 2 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 2.0, p95 2.0, IQR [2.0, 2.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] |
| `b08_cycle` | divergent(8) | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] |
| `b09_thesis` | 3 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] |
| `b10_random` | divergent(8) | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 1.0, p95 1.0, IQR [1.0, 1.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] |
| `b11_width` | oscillating | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 6.0, p95 6.0, IQR [6.0, 6.0] |
| `b12_float` | oscillating | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 6.0, p95 6.0, IQR [6.0, 6.0] |
| `b13_varioref` | oscillating | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 6.0, p95 6.0, IQR [6.0, 6.0] |
| `b14_ifthen` | oscillating | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 8.0, p95 8.0, IQR [8.0, 8.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] |
| `b15_ibid` | 3 | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 1.0, p95 1.0, IQR [1.0, 1.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 3.0, p95 3.0, IQR [3.0, 3.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] | median 0.0, p95 0.0, IQR [0.0, 0.0] |

## Gate 1

| Gate 1 check | Pass | Observed |
|---|---|---|
| b08 observed AMPLIFYING | PASS | AMPLIFYING |
| b05 not AMPLIFYING | PASS | CERTIFIED |
| b11_width matches declared false negative (CERTIFIED) | PASS | CERTIFIED |
| b12_float matches declared false negative (CERTIFIED) | PASS | CERTIFIED |
| b13_varioref matches declared false negative (CERTIFIED) | PASS | CERTIFIED |
| b07_footnote UNKNOWN | PASS | UNKNOWN |
| b15_ibid UNKNOWN | PASS | UNKNOWN |

**Gate 1: PASS**

## Gate 2 (EC1)

| Document | Predicted N | Ground truth N* | N* <= N | Declared failure? |
|---|---|---|---|---|
| `b01_plain` | 1 | 1 | yes | no |
| `b02_backref` | 2 | 2 | yes | no |
| `b03_fwdref` | 2 | 2 | yes | no |
| `b04_chain` | 3 | 2 | yes | no |
| `b05_toc` | 3 | 3 | yes | no |
| `b06_bib` | 4 | 3 | yes | no |
| `b09_thesis` | 4 | 3 | yes | no |
| `b11_width` | 2 | divergent(8) | NO | yes |
| `b12_float` | 2 | divergent(8) | NO | yes |
| `b13_varioref` | 2 | divergent(8) | NO | yes |

**Gate 2 (EC1): PASS** -- every EC1 violation is a declared false negative (b11_width, b12_float, b13_varioref)
