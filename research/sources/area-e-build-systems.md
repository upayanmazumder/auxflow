# Build Systems

Search area E: build-system research. Audit date 2026-08-27.

Scope: establish (a) whether the static-versus-dynamic dependency information gap is
already well studied in build systems, (b) whether any build-system work statically
bounds the number of iterations to a fixpoint, (c) whether any build-system work
classifies cyclic build dependencies as benign versus divergent, and (d) which item is
the most dangerous prior art for AuxFlow.

Tooling note for reproducibility: in this environment `bash`/`curl` had no network
access and `dblp.org/rec/*` plus `dblp.org/search/publ/api` were unreachable (socket
resets). All bibliographic verification below was therefore done against the
**Crossref REST API** (`https://api.crossref.org/works/<DOI>`), which is authoritative
for title, authors, container, volume, pages, and year. Every DOI in this file was
resolved through Crossref and matched against the fetched full text.

---

## Search log

### Microsoft Research (primary PDF host)
query    : `https://www.microsoft.com/en-us/research/uploads/prod/2018/03/build-systems.pdf`
examined : full text, 29 pages, read in full
outcome  : Build Systems a la Carte (ICFP 2018). Obtained the applicative-vs-monadic
           task definition verbatim, plus S2.1 (Make/static), S3.6 (correctness under
           acyclicity), S6.5 (self-tracking), S6.6 (Iterative Computations - explicitly
           discusses LaTeX, fixed points, and bounding the number of executions).
status   : SOURCED

### Cambridge Core (JFP landing page)
query    : `https://www.cambridge.org/core/journals/journal-of-functional-programming/article/build-systems-a-la-carte-theory-and-practice/097CE52C750E69BD16B78C318754C7A4`
examined : metadata block (article body behind a service-disruption banner)
outcome  : Confirmed the extended journal version: JFP vol 30, article e11,
           DOI 10.1017/S0956796820000088, online 2020-04-21.
status   : SOURCED (metadata)

### ndmitchell.com (author copy of JFP version)
query    : `https://ndmitchell.com/downloads/paper-build_systems_a_la_carte_theory_and_practice-21_apr_2020.pdf`
examined : full text, 55 pages
outcome  : Open-access author copy of the JFP 2020 version. Confirmed S8.5 "Iterative
           computations" is the renumbered S6.6 with essentially identical wording; the
           LaTeX / bistable / diverging sentence survives unchanged into the journal
           version. Also confirmed the paper's own list of changes vs ICFP.
status   : SOURCED

### api.crossref.org
query    : `https://api.crossref.org/works/10.1145/3236774`
examined : 1 record
outcome  : "Build systems à la carte", Mokhov / Mitchell / Peyton Jones, Proc. ACM
           Program. Lang. vol 2, issue ICFP, pages 1-29, published 2018-07-30, ACM.
status   : SOURCED

### api.crossref.org
query    : `https://api.crossref.org/works/10.1145/2814270.2814316`
examined : 1 record
outcome  : "A sound and optimal incremental build system with dynamic dependencies",
           Erdweg / Lichter / Weiel (all TU Darmstadt), OOPSLA 2015 proceedings, pages
           89-106, SPLASH '15, Pittsburgh, 2015-10-23.
status   : SOURCED

### pluto-build.github.io -> Marburg author mirror
query    : `https://pluto-build.github.io/` then
           `https://www.mathematik.uni-marburg.de/~seba/publications/pluto-incremental-build.pdf`
examined : project page + full author's-version PDF (~14 pages of extracted text)
outcome  : Obtained the Pluto paper in full. The `erdweg.org` and
           `web.archive.org` routes both failed (301 to a dead uni-mainz path and a
           binary-fetch abort respectively); the Marburg mirror served the PDF.
           This is the single most important find in this area - see below.
status   : SOURCED

### api.crossref.org
query    : `https://api.crossref.org/works/10.1145/2364527.2364538`
examined : 1 record
outcome  : "Shake before building" (subtitle "replacing make with haskell"),
           Neil Mitchell, ICFP'12, Copenhagen, pages 55-66, 2012-09-09.
           Task brief's DOI confirmed correct.
status   : SOURCED

### ndmitchell.com
query    : `https://ndmitchell.com/downloads/paper-shake_before_building-10_sep_2012.pdf`
examined : full text
outcome  : Shake paper author copy. Key finding at S2.2: for dynamic (Rule_s) build
           systems "there is no obvious way to determine if the expression is
           well-defined in advance". Shake has no fixpoint or cycle machinery.
status   : SOURCED

### gittup.org
query    : `http://gittup.org/tup/build_system_rules_and_algorithms.pdf`
examined : full text, 27 pages
outcome  : Mike Shal, "Build System Rules and Algorithms", 2009. Tech report EXISTS and
           is live at that URL (redirects to https). Establishes the Alpha/Beta build
           system distinction and the O(n) vs O(log^2 n) claim. Grepped for
           cycle/iterate/converge/fixpoint/latex: no iteration or fixpoint concept
           anywhere; strictly DAG-based.
status   : SOURCED

### api.crossref.org
query    : `https://api.crossref.org/works/10.1002/spe.4380090402`
examined : 1 record
outcome  : Feldman, "Make - a program for maintaining computer programs", Software:
           Practice and Experience 9(4):255-265, April 1979.
status   : SOURCED

### api.crossref.org
query    : `https://api.crossref.org/works/10.1007/978-3-642-19440-5_26`
examined : 1 record
outcome  : Erdweg & Ostermann, "Featherweight TeX and Parser Correctness", SLE 2010,
           LNCS 6563, pages 397-416, Springer (printed 2011). This is Pluto's
           reference [4], the citation backing its undecidability claim about LaTeX.
status   : SOURCED

### api.crossref.org
query    : `https://api.crossref.org/works/10.1145/3428237`
examined : 1 record
outcome  : Spall / Mitchell / Tobin-Hochstadt, "Build scripts with perfect
           dependencies", Proc. ACM Program. Lang. vol 4, issue OOPSLA, pages 1-28,
           2020-11-13. Tracing-based dependency capture (the Rattle system).
status   : SOURCED

### microsoft.com research
query    : `https://www.microsoft.com/en-us/research/wp-content/uploads/2016/03/hadrian.pdf`
examined : full text
outcome  : Mokhov / Mitchell / Peyton Jones / Marlow, "Non-recursive Make Considered
           Harmful: Build Systems at Scale", Haskell 2016. Establishes GHC's use of
           explicit build PHASES plus "Make's automatic restarting feature", reduced by
           hand to three phases. A hand-derived, not computed, bound on build rounds.
status   : SOURCED

### stackoverflow.com (via Stack Exchange API)
query    : `https://stackoverflow.com/questions/14622169/how-to-write-fixed-point-build-rules-in-shake-e-g-latex`
examined : question + 2 answers
outcome  : Mitchell (2013), the reference Mokhov et al. cite as the recommended
           encoding for LaTeX. Explicit: "calling Latex repeatedly does not always
           produce a fixed point, so make sure you have a bound on the iterations".
           The bound in the sample code is the hardcoded constant `i > 100`.
status   : SOURCED

### aegis.sourceforge.net (Miller's own site)
query    : `https://aegis.sourceforge.net/auug97.pdf`, grep
           `(?i)upper bound|number of passes|two passes|Repetition|guarantee`
examined : full text, S3.3.2 "Repetition"
outcome  : Peter Miller, "Recursive Make Considered Harmful". THE closest thing in the
           build-systems literature to a graph-structural bound on the number of build
           passes. Quoted verbatim below. Independently re-verified by me after a
           subagent surfaced it.
status   : SOURCED

### gnu.org
query    : `https://www.gnu.org/software/make/manual/html_node/Remaking-Makefiles.html`,
           grep `(?i)MAKE_RESTARTS|clean slate|infinite loop|restart`
examined : GNU Make Manual S3.5 "How Makefiles Are Remade"
outcome  : GNU Make genuinely restarts its whole parse-and-plan cycle when a remade
           makefile changed. `MAKE_RESTARTS` counts restarts. NO numeric bound; only
           two named escape hatches against literal infinite loops.
status   : SOURCED

### ninja-build.org
query    : `https://ninja-build.org/manual.html`, grep `restat`
examined : Ninja manual v1.13.1, full text (two passes)
outcome  : `restat` re-stats outputs after execution and suppresses downstream
           propagation. No loop-until-stable feature, no fixpoint concept, no
           convergence concept documented anywhere in the manual.
status   : SOURCED

### bazel.build
query    : `https://bazel.build/reference/command-line-reference`, grep `include_scanning`;
           `https://bazel.build/docs/bazel-and-cpp`
examined : Bazel command-line reference + "C++ and Bazel" page
outcome  : `--cc_include_scanning` / `--experimental_unsupported_and_brittle_include_scanning`
           both default to false and are documented as unsound. `layering_check` and
           `parse_headers` are validation, not prediction.
status   : SOURCED

### api.crossref.org
query    : `https://api.crossref.org/works/10.1109/ICSE.2019.00125`
examined : 1 record
outcome  : Licker & Rice, "Detecting Incorrect Build Rules", ICSE 2019, Montreal,
           pages 1234-1244, IEEE. NOTE: the DOI in the task brief
           (10.1109/ICSE.2019.00109) resolves to a DIFFERENT paper (FOCUS, an API
           recommender system). Corrected DOI verified twice, independently.
status   : SOURCED (with correction)

### api.crossref.org
query    : `https://api.crossref.org/works/10.1109/ICSM.2007.4362678`
examined : 1 record
outcome  : Adams / Tromp / de Schutter / de Meuter, "MAKAO", ICSM 2007, Paris, pages
           517-518 (the 2-page tool demo). NOTE: the DOI in the task brief
           (10.1109/ICSM.2007.4362624) is the SEPARATE full paper "Design recovery and
           maintenance of build systems", ICSM 2007 pages 114-123. Both are real; they
           are different papers. Corrected and independently re-verified.
status   : SOURCED (with correction)

### api.crossref.org and Springer
query    : `https://api.crossref.org/works/10.1007/s10664-017-9510-8`
examined : 1 record + Springer abstract
outcome  : Bezemer / McIntosh / Adams / German / Hassan, "An empirical study of
           unspecified dependencies in make-based build systems", Empirical Software
           Engineering 22(6):3117-3148, 2017. Task brief's DOI confirmed correct.
status   : SOURCED

### ieeexplore.ieee.org and api.crossref.org
query    : `https://api.crossref.org/works/10.1109/ICSE.2012.6227152` and
           `https://api.crossref.org/works/10.1145/2351676.2351749`
examined : 2 records + IEEE Xplore abstract page
outcome  : SYMake exists in two forms: "Build code analysis with symbolic evaluation",
           ICSE 2012 pages 650-660 (full paper), and "SYMake: a build code analysis and
           refactoring tool for makefiles", ASE 2012 pages 366-369 (tool demo).
status   : SOURCED

### gangfan.github.io + api.crossref.org
query    : `https://api.crossref.org/works/10.1145/3395363.3397388` + author PDF
examined : full text
outcome  : VeriBuild (Fan et al., ISSTA 2020, pages 463-474). Its related-work section
           taxonomises the ENTIRE build-dependency-analysis literature as
           static/dynamic/hybrid techniques for missing and redundant dependencies -
           never iteration counts, never convergence. Valuable as a survey admission.
status   : SOURCED

### chenbihuan.github.io
query    : `https://chenbihuan.github.io/paper/ase20-chen-buildfast.pdf`
examined : full text
outcome  : BuildFast (ASE 2020). Predicts a CATEGORICAL build outcome (passed / errored
           / failed) from git and CI history metadata. No iteration-count target
           variable exists anywhere in its feature or label tables.
status   : SOURCED

### web_search
query    : `build system research "idempotent build" OR "build convergence" OR "repeated builds until fixpoint" bounding number of build rounds graph diameter`
examined : ~99 results
outcome  : NOTHING RELEVANT to build systems. Every substantive hit was generic
           lattice/dataflow fixpoint theory (Kleene, Knaster-Tarski, monotone
           frameworks, lattice-height bounds O(N*h)) - i.e. attribute-grammar and
           abstract-interpretation territory, not build systems. No build-system paper
           bounds rebuild rounds by graph structure.
status   : SOURCED (as a negative)

### web_search
query    : `"build system" research statically bound "number of iterations" OR "number of rounds" rebuild fixpoint SCC longest path prediction`
examined : ~60 results
outcome  : NOTHING RELEVANT. Hits were topological-sort tutorials, critical-path
           project-management pages, and one unrelated Python type-inference tool.
status   : SOURCED (as a negative)

### web_search
query    : `build system OR incremental computation classify cyclic dependencies "benign" versus divergent terminating cycle static analysis guarantee fixpoint reached`
examined : ~40 results
outcome  : NOTHING RELEVANT in build systems. General monotone-framework material only.
           No benign-vs-divergent cycle taxonomy found in any build-system work.
status   : SOURCED (as a negative)

### web_search
query    : `"build system" termination analysis prove build terminates static guarantee number of passes document compilation predict`
examined : ~27 results
outcome  : NOTHING RELEVANT. Results were CompCert-style verified-compiler material and
           the acyclic-dependencies principle. Confirms build-system termination is
           universally obtained by ASSUMING acyclicity, not by analysis.
status   : SOURCED (as a negative)

### web_search
query    : `Erdweg Lichter cyclic build dependencies build system "cycle" sound incremental follow-up paper` and
           `"cyclic build dependencies" "fixpoint" build system paper`
examined : ~18 results
outcome  : No follow-up paper on cyclic builds by this group was found. Cycle support is
           contained entirely within the OOPSLA 2015 Pluto paper itself (S3.4, S4.6,
           S5.2). Searches surfaced only the 2015 paper and secondary commentary.
status   : SOURCED (as a negative on the follow-up)

---

## Verified sources

### 1. Mokhov, Mitchell, Peyton Jones - Build Systems a la Carte (ICFP 2018)

- **Citation**: Andrey Mokhov, Neil Mitchell, Simon Peyton Jones. "Build systems à la
  carte." Proceedings of the ACM on Programming Languages, Volume 2, Issue ICFP,
  Article 79, pages 1-29 (29 pages). ACM, September 2018.
- **DOI / URL**: `10.1145/3236774` -
  https://www.microsoft.com/en-us/research/uploads/prod/2018/03/build-systems.pdf
- **Access**: Full text (CC-BY, open access).

- **Verbatim quote - the task abstraction (S3.2)**:
  > `newtype Task c k v = Task { run :: forall f. c f => (k -> f v) -> f v }`
  > `type Tasks c k v = k -> Maybe (Task c k v)`

- **Verbatim quote - the applicative/monadic distinction (S3.4)**:
  > "But now that it has emerged, we find that constraints c classify task descriptions
  > in a very interesting way: • Task Applicative. In sprsh1 we needed only Applicative
  > operations, expressing the fact that the dependencies between cells can be
  > determined statically; that is, by looking at the formulae, without 'computing' them
  > (see §3.7). • Task Monad. As we shall see in §3.5, a monadic task allows dynamic
  > dependencies, in which a formula may depend on cell C, but which cell C depends on
  > the value of another cell D."

- **Verbatim quote - monadic == dependencies computed from values (S3.5)**:
  > "As explained in §2.2, some task descriptions have dynamic dependencies, which are
  > determined by values of intermediate computations. In our framework, such task
  > descriptions correspond to the type Tasks Monad k v."

  And, confirming that static extraction is impossible for the monadic case (S3.7):
  > "So much for applicative tasks. What about monadic tasks with dynamic dependencies?
  > As we have seen in §2.3, dynamic dependencies need to be tracked too. This cannot be
  > done statically; notice that we cannot apply the function dependencies to a Task
  > Monad because the Const functor has no Monad instance."

- **Verbatim quote - a trivial static execution bound for DAGs (S2.1)**:
  > "Note that if the dependency graph is acyclic then each task needs to be executed at
  > most once. Cyclic task dependencies are typically not allowed in build systems but
  > there are rare exceptions, see §6.6."

- **Verbatim quote - correctness requires acyclicity (S3.6)**:
  > "It is hard to satisfy the above definition of correctness given a task description
  > with cycles. All build systems discussed in this paper are correct only under the
  > assumption that the given task description is acyclic. This includes the busy build
  > system introduced earlier: it will loop indefinitely given a cyclic tasks."

- **Verbatim quote - early cutoff (S2.3)**:
  > "Shake also supports the early cutoff optimisation. When it executes a task and the
  > result is unchanged from the previous build, it is unnecessary to execute the
  > dependent tasks, and hence Shake can stop a build earlier, as illustrated in Fig. 3.
  > Not all build systems support early cutoff: Make and Excel do not, whereas Shake and
  > Bazel (introduced below) do."

- **Verbatim quote - self-tracking (S6.5)**:
  > "Some build systems, for example Excel and Ninja, are capable of recomputing a task
  > if either its dependencies change, or the task itself changes. ... The build systems
  > that have precise self-tracking are all ones which use a non-embedded domain specific
  > language to describe build tasks. Those which use a full programming language, e.g.
  > Shake, are faced with the challenge of implementing equality on arbitrary task
  > functions."

- **Verbatim quote - S6.6 "Iterative Computations", THE critical passage**:
  > "Some computations are best described not by a chain of acyclic dependencies, but by
  > a loop. For example, LATEX requires repeated rebuilding until it reaches a fixed
  > point, which can be directly expressed in build systems, such as Pluto [Erdweg et al.
  > 2015]. Another example is Excel, where a cell can depend on itself, for example: A1 =
  > A1 + 1. In such cases Excel will normally not execute anything, but if the 'Iterative
  > Calculations' feature is enabled Excel will execute the formula for a specified
  > maximum number N of times per calculation (where N is a setting that defaults to 100)."
  >
  > "For examples like LATEX we consider the proper encoding to not be circular tasks,
  > but a series of iterative steps, as described by Mitchell [2013]. It is important
  > that the number of executions is bounded, otherwise the build system may not
  > terminate (a legitimate concern with LATEX, which can be put into a situation where
  > it is bistable or diverging over multiple executions)."
  >
  > "Overall we choose not to deal with cyclic dependencies, a choice that most build
  > systems also follow. There are computation frameworks that support tasks with cyclic
  > dependencies under the assumption that tasks are monotonic in a certain sense, e.g.
  > see [Pottier 2009] and [Radul 2009]."

- **Exact contribution**: A formal, executable (Haskell) framework decomposing any build
  system into a *scheduler* (topological / restarting / suspending) crossed with a
  *rebuilder* (dirty bit / verifying traces / constructive traces / deep constructive
  traces). Defines minimality and correctness precisely. The `Task c k v` type with a
  constraint parameter `c` makes the static-versus-dynamic dependency question a
  *type-level* distinction: `Applicative` = statically extractable dependencies,
  `Monad` = dependencies computed from fetched values.

- **What it does NOT do**: It does not analyse task bodies. `dependencies` extracts a
  static dependency list by *running* an applicative task in the `Const` functor - it is
  a polymorphism trick, not a source-level static analysis, and it provably cannot work
  for monadic tasks. It performs no fixpoint-depth analysis, computes no pass numbers,
  and derives no iteration bound. It explicitly *requires* the number of executions to
  be bounded but supplies no method for obtaining that bound; and it explicitly declines
  to handle cyclic dependencies at all. It names LaTeX bistability and divergence as a
  hazard without offering any means to detect either.

- **Relevance to AuxFlow**: Anticipates AuxFlow's *vocabulary and framing* completely -
  static vs dynamic dependencies, the observation that LaTeX is a fixpoint computation,
  the observation that LaTeX can be bistable or diverging, and the requirement that
  iteration be bounded. AuxFlow MUST cite this and MUST NOT claim to have noticed that
  LaTeX is a fixpoint problem or that it can diverge. AuxFlow's actual claim has to be
  narrower: it *derives* the bound and *classifies* the divergence risk that this paper
  merely names.

- **Anticipation verdict**: PARTIAL OVERLAP. Full anticipation of the framing and the
  problem statement; zero anticipation of a static analysis producing a bound or a
  classification.
- **Evidence label**: SOURCED

---

### 2. Mokhov, Mitchell, Peyton Jones - Build Systems a la Carte: Theory and Practice (JFP 2020)

- **Citation**: Andrey Mokhov, Neil Mitchell, Simon Peyton Jones. "Build systems à la
  carte: Theory and practice." Journal of Functional Programming, Volume 30, article
  e11, 55 pages. Cambridge University Press, 2020. Published online 21 April 2020.
- **DOI / URL**: `10.1017/S0956796820000088` -
  https://ndmitchell.com/downloads/paper-build_systems_a_la_carte_theory_and_practice-21_apr_2020.pdf
  (open-access author copy; Cambridge Core landing page was serving a service-disruption
  banner in place of the article body at audit time, so the metadata came from the
  landing page and the full text from the author copy.)
- **Access**: Full text (CC-BY, open access) via author copy; metadata via publisher.

- **Verbatim quote - the paper's own statement of what changed**:
  > "This paper is an extended version of an earlier conference paper (Mokhov et al.,
  > 2018). The key changes compared to the earlier version are (i) we added further
  > clarifications and examples to Section 3, and in particular, Section 3.8 is entirely
  > new; (ii) Sections 4 and 5 are based on the material from the conference paper but
  > have been substantially expanded ...; (iii) Section 7 is completely new; (iv)
  > Sections 8.1, 8.6, 8.7, 8.8, and 8.9 are almost entirely new, and Section 8.3 has
  > been revised."

- **Verbatim quote - S8.5 "Iterative computations" (the renumbered S6.6)**:
  > "Some computations are best described not by a chain of acyclic dependencies, but by
  > a loop. For example, LATEX requires repeated rebuilding until it reaches a fixed
  > point, which can be directly expressed in build systems, such as PLUTO (Erdweg et
  > al., 2015)."
  >
  > "For example like LATEX, we consider the proper encoding to not be circular tasks,
  > but a series of iterative steps, as described by Mitchell (2013). It is important
  > that the number of executions is bounded, otherwise the build system may not
  > terminate (a legitimate concern with LATEX, which can be put into a situation where
  > it is bistable or diverging over multiple executions)."
  >
  > "We choose not to deal with cyclic dependencies - a choice that most build systems
  > also follow. There are computation frameworks that support dependency cycles under
  > the assumption that tasks are monotonic in a certain sense (Pottier, 2009; Radul,
  > 2009)."

- **Exact contribution**: The definitive, extended version of the framework. Section 7
  (new) covers the practical Cloud Shake experience.

- **What it does NOT do**: Section 8.5 is *materially unchanged* from ICFP S6.6. Despite
  55 pages and two extra years, the authors added nothing on bounding iterations,
  classifying cycles, or analysing LaTeX. The LaTeX position is stable across both
  versions.

- **Relevance to AuxFlow**: Cite the JFP version as canonical. Its stability across
  versions is itself evidence: the leading formal treatment of build systems has looked
  directly at LaTeX-as-fixpoint twice and declined to analyse it both times. That is a
  defensible statement of the gap AuxFlow occupies.

- **Anticipation verdict**: PARTIAL OVERLAP (identical to the ICFP version).
- **Evidence label**: SOURCED

---

### 3. Erdweg, Lichter, Weiel - Pluto (OOPSLA 2015)  ***MOST DANGEROUS***

- **Citation**: Sebastian Erdweg, Moritz Lichter, Manuel Weiel. "A sound and optimal
  incremental build system with dynamic dependencies." In Proceedings of the 2015 ACM
  SIGPLAN International Conference on Object-Oriented Programming, Systems, Languages,
  and Applications (OOPSLA '15), pages 89-106. ACM, 23 October 2015. SPLASH '15,
  Pittsburgh, PA, USA.
- **DOI / URL**: `10.1145/2814270.2814316` -
  https://www.mathematik.uni-marburg.de/~seba/publications/pluto-incremental-build.pdf
  (author's version). Project site: https://pluto-build.github.io/
- **Access**: Full text via author's version, including the appendix.

- **Verbatim quote - what "sound" and "optimal" mean (abstract)**:
  > "A build system must be sound (after a build, generated files consistently reflect
  > the latest source files) and efficient (recheck and rebuild as few build units as
  > possible)."

- **Verbatim quote - the formal soundness criteria (S4.3-S4.4)**. Soundness is stated as
  three criteria (S1)-(S3), of which the paper states:
  > "(S3) If build((b, i), ω0) = (u, ω), then all u ∈ u are totally consistent with
  > respect to ω."

  and optimality as two incrementality properties:
  > "(I1) Minimize the number of builder-function executions." ... "An incremental build
  > system is optimal if, for any input, it executes the minimal number of builders (I1)
  > and checks internal consistency as infrequently as possible (I2), where (I1) takes
  > precedence over (I2). As a corollary, an optimal build system is idempotent when the
  > file system is unchanged."

- **Verbatim quote - dependency discovery is interleaved with execution (abstract)**:
  > "To support dynamic dependencies, our rebuild algorithm interleaves dependency
  > analysis and builder execution and enforces invariants on the dependency graph
  > through a dynamic analysis."

- **Verbatim quote - THE most dangerous sentence for AuxFlow (S3.3, "Dynamic
  dependencies")**. NOTE: this paragraph is interleaved with figure text in the
  two-column PDF extraction; the reconstructed running sentence, verified against the
  raw extraction, is:
  > "Dynamic dependencies. Often, static dependency detection is difficult. In the case
  > of Latex where even parsing is undecidable [4], soundly detecting dependencies is a
  > lost cause. Therefore, in pluto, we support the dynamic discovery of dependencies,
  > which a builder can register at any time during a build using methods require and
  > provide."

  Reference [4] is verified as: S. Erdweg and K. Ostermann, "Featherweight TeX and Parser
  Correctness", SLE 2010, LNCS 6563, pages 397-416, Springer.
  DOI `10.1007/978-3-642-19440-5_26` (Crossref-verified).

- **Verbatim quote - LaTeX needs repeated building (S3.2)**:
  > "For the aux file, there is another reason for using a file hash as a stamp, namely
  > Latex requires repeated building until the content of the aux file stabilizes
  > (details in Section 3.4)."

- **Verbatim quote - the aux-file self-cycle and the LaTeX/BibTeX cycle (S3.4)**:
  > "In our example, there are actually two cycles. First, the Latex builder is in a
  > cycle by itself because it reads from and writes to the same aux file. Second, the
  > Latex and Bibtex builders depend on each other because the Latex builder writes to
  > the aux file that Bibtex reads and Bibtex writes to the bbl file that Latex reads."
  >
  > "Without cycle support, we would have to merge the Latex and Bibtex builders into a
  > single builder, which itself has to make sure that Latex runs often enough and that
  > Bibtex is not called on every single run but only when actually needed."

- **Verbatim quote - the fixpoint cycle handler, and its explicit disclaimer (S3.4)**:
  > "Fixpoint cycle handler. This cycle handler invokes the builders in the cycle
  > iteratively until they stabilize, that is, until a fixpoint is reached. In each
  > iteration, the cycle handler checks which builders in the cycle need to be reinvoked
  > because some dependencies are not up-to-date. The handler then invokes these
  > builders. If no builder required invocation, the building reached a fixpoint and the
  > cycle building stops. If at least one builder was invoked, the cycle handler starts
  > the next iteration. **It is important to note that the fixpoint cycle handler itself
  > does not guarantee a fixpoint will be reached. The builders in the cycle need to be
  > designed to take part in a fixpoint compilation.**" (emphasis added)

- **Verbatim quote - the second predefined handler (S3.4/S4)**:
  > "Build-at-once cycle handler. This cycle handler collects all the input of the cyclic
  > builders and builds them simultaneously by invoking a single builder on the collected
  > input."

- **Verbatim quote - cycle handling is user-supplied, not inferred (S3.4)**:
  > "When pluto detects a build cycle, it queries all builders in the cycle for a cycle
  > handler. If none of the builders provides a cycle handler, the cycle cannot be built
  > and building is aborted. Otherwise, pluto asks each cycle handler whether it can
  > build this particular cycle (method canBuildCycle)."
  >
  > "In general, there is no one correct way of handling cycles and different builders
  > require different cycle-handling strategies."

- **Verbatim quote - fact-granularity dependency on the aux file (S3.2)**:
  > "To this end, the Bibtex builder uses a custom stamper that parses the aux file,
  > extracts the bibliography name and the set of referenced citation keys, and uses them
  > as a stamp. Accordingly, the Bibtex builder only becomes outdated when a different
  > bibliography is used or a different set of bibliography entries is cited in the aux
  > file. For example, changes to regular text or to captions of figures do not lead to a
  > rebuild of the Bibtex builder."

- **Verbatim quote - on latexmk (S7, related work)**:
  > "Even Latex-specific build systems like latexmk use unsound heuristics to detect
  > dependencies."

- **Exact contribution**: A build system (Java API, ~25 builders implemented) with
  dynamically discovered file and builder dependencies, user-selectable *file stampers*
  that let a consumer declare a dependency on a semantic *part* of a file's content
  rather than the whole file, automatic metadependencies on builder implementations, and
  first-class support for cyclic builder dependencies via pluggable cycle handlers. It
  provides a formal two-layered dependency-graph model and machine-checked-style proofs
  of soundness (Theorem 5.3) and optimality relative to the previous dependency graph.
  Its running example throughout the paper is **a LaTeX + BibTeX builder**.

- **What it does NOT do**: Everything is dynamic. It never parses the `.tex` source. It
  detects cycles at runtime, and having detected one it *asks the developer* which
  strategy to apply - it does not classify the cycle. The fixpoint handler is an
  iterate-until-stable loop with an explicit, printed disclaimer that convergence is not
  guaranteed and is the builder author's responsibility. There is no pass-number
  concept, no static bound on iterations, no taint analysis, no notion of a fact
  influencing how much content the document generates, and no benign-versus-amplifying
  distinction. It also has no static diagnosis: when a cycle fails to converge, Pluto
  reports nothing about *which fact* is responsible.

- **Relevance to AuxFlow**: This is the closest prior art in existence and it is
  dangerous on four separate axes.
  1. **Same problem domain, same example.** Pluto's marquee example IS the LaTeX/BibTeX
     build with the aux-file cycle. AuxFlow cannot claim to have identified the aux-file
     self-cycle or the LaTeX/BibTeX cycle; Erdweg et al. did in 2015.
  2. **Same iterate-to-fixpoint mechanism.** The `FixpointCycleHandler` is exactly the
     dynamic convergence loop AuxFlow proposes to be evaluated against.
  3. **Anticipates the fact-granularity intuition, dynamically.** The custom aux stamper
     that parses the `.aux` file and reduces it to the set of cited keys is, in spirit,
     an instance-level fact dependency - it is *finer than the file* and it is
     *semantic*. AuxFlow's "instance-level fact node" idea is therefore NOT novel as an
     idea about granularity; what is unclaimed is deriving those instances *statically
     from the source*, and assigning them pass numbers.
  4. **Most dangerous of all: it explicitly considered AuxFlow's approach and published
     a reason to reject it.** "In the case of Latex where even parsing is undecidable,
     soundly detecting dependencies is a lost cause." A top-tier PL paper, by the author
     of the Featherweight TeX parser-correctness paper, states on the record that static
     dependency detection for LaTeX is not worth attempting. AuxFlow's *only* answer to
     this is its declared subset - and that answer must be stated explicitly, up front,
     and defended, because a reviewer who knows this paper will raise it immediately.
     AuxFlow must not present static analysis of LaTeX as an unconsidered opportunity;
     it must present it as a re-opening of a question that was closed for stated reasons,
     with the subset restriction as the reason it is now tractable.

- **Anticipation verdict**: PARTIAL OVERLAP, at the outer limit of partial. Full
  anticipation of: the LaTeX aux cycle, cyclic build dependencies as a first-class
  feature, iterate-to-fixpoint as the resolution mechanism, sub-file semantic dependency
  granularity, and the explicit acknowledgement that convergence is not guaranteed. NOT
  anticipated: any static analysis, any derived bound, any classification of a cycle as
  benign or amplifying, any source-level diagnosis.
- **Evidence label**: SOURCED

---

### 4. Mitchell - Shake Before Building (ICFP 2012)

- **Citation**: Neil Mitchell. "Shake before building: replacing make with haskell." In
  Proceedings of the 17th ACM SIGPLAN International Conference on Functional Programming
  (ICFP '12), pages 55-66. ACM, 9 September 2012. Copenhagen, Denmark.
- **DOI / URL**: `10.1145/2364527.2364538` (Crossref-verified; the task brief's DOI is
  correct) - https://ndmitchell.com/downloads/paper-shake_before_building-10_sep_2012.pdf
- **Access**: Full text (author's version).

- **Verbatim quote - dynamic dependencies (S1)**:
  > "The key difference from make (and nearly all other build tools) is that rather than
  > specifying all dependencies in advance, we allow further dependencies to be specified
  > after examining the results of previous dependencies."

- **Verbatim quote - rejecting the static graph (S2)**:
  > "However, any approach based on a static dependency graph cannot permit additional
  > dependencies to be specified while running the rules. As we saw in §1, many examples
  > require additional dependencies to be specified while running the rules. The solution
  > is simple - we reject the idea that build tools should use a static dependency graph."

- **Verbatim quote - the decidability boundary (S2.2), the key passage for AuxFlow**:
  > "A Rule_m build system is able to produce the result for a given target iff the
  > expression build_m rules target is well-defined. If we assume all actions are total,
  > then this expression is well-defined if you can build a finite dependency graph for
  > the target with the available rules. **This property can be checked without running
  > any actions.**"
  >
  > "As before, a Rule_s build system is able to produce a result for a given target iff
  > the expression build_s rules target is well-defined. **However, unlike before, there
  > is no obvious way to determine if the expression is well-defined in advance without
  > detailed information about the action functions.**" (emphasis added)

- **Exact contribution**: Shake - a Haskell-embedded build library with dynamic
  dependencies (`need` called mid-rule), a persistent database of the previous
  dependency graph, minimal rebuilds via stored `built`/`changed` times, and the
  unchanging-result optimisation (the origin of early cutoff). Deployed at scale
  (30,000+ build objects, >1M lines).

- **What it does NOT do**: No cycle support at all - Pluto's related work confirms
  "Shake ... aborts execution when detecting a cycle." No fixpoint machinery, no
  iteration bound, no static analysis of rule bodies.

- **Relevance to AuxFlow**: The S2.2 passage is the cleanest statement in the
  build-systems literature of the exact boundary AuxFlow is trying to cross. Mitchell
  says: for *static* rules you can decide buildability without running anything; for
  *dynamic* rules you cannot, absent "detailed information about the action functions."
  AuxFlow's declared LaTeX subset is precisely an attempt to supply that detailed
  information. This is a useful framing for AuxFlow to adopt honestly, and it is also a
  warning: the phrase "no obvious way" is a decidability caveat, not an impossibility
  proof, but AuxFlow inherits the burden of showing its subset restores decidability.

- **Anticipation verdict**: INFORMS ONLY. Anticipates the framing of the
  static-vs-dynamic decidability boundary; anticipates none of AuxFlow's machinery.
- **Evidence label**: SOURCED

---

### 5. Shal - Build System Rules and Algorithms (Tup tech report, 2009)

- **Citation**: Mike Shal. "Build System Rules and Algorithms." Unpublished technical
  report, 2009. 27 pages.
- **DOI / URL**: No DOI (self-published technical report). VERIFIED LIVE at
  http://gittup.org/tup/build_system_rules_and_algorithms.pdf (redirects to https).
  Independently corroborated as a real, citable document by its appearance in the
  reference lists of both Mitchell ICFP 2012 (ref 12: "Mike Shal. Build system rules and
  algorithms. http://gittup.org/tup/build_system_rules_and_algorithms.pdf 2009") and
  Erdweg et al. OOPSLA 2015 (ref 16, Crossref-visible as "Shal, M., Build system rules
  and algorithms, 2009").
- **Access**: Full text.

- **Verbatim quote - the three rules (S2)**:
  > "1. Scalability: Given an already up-to-date system, applying a change to the system
  > and building it should take time that is proportionate to the changes required to
  > bring the system up to date. 2. Correctness: Given an up-to-date system in state X,
  > applying change A and updating the system may result in state Y. Undoing change A and
  > performing an update must return the system to state X. 3. Usability: There must not
  > be different ways of building the system that the user must remember in order to
  > accommodate rules 1) or 2)."

- **Verbatim quote - the DAG assumption is universal and unchallenged (S1)**:
  > "However, the core algorithms used by these build systems haven't really evolved
  > since the original directed acyclic graph (DAG) processing ones introduced by make 30
  > years ago."

- **Exact contribution**: Establishes the Alpha (global DAG, O(n) update) versus Beta
  (partial DAG, O(log^2 n) update) taxonomy, and the argument that a scalable build
  system must be given the list of changed files up front rather than scanning. This is
  the design basis for Tup.

- **What it does NOT do**: Grepped the full text for cycle / cyclic / iterate / converge
  / fixpoint / repeat / circular / latex. There is NO iteration concept, NO fixpoint
  concept, and NO cycle handling anywhere in the document. "Cycle" appears only in the
  phrase "Edit-Compile-Test cycle". Tup is strictly a DAG system in which each node is
  updated at most once. Its notion of "correctness" is state-reversibility under undo,
  which is orthogonal to convergence.

- **Relevance to AuxFlow**: Confirms that the highest-performance branch of build-system
  design doubled down on the acyclic single-pass assumption rather than relaxing it.
  Useful for AuxFlow's related work as evidence that the DAG assumption is the field's
  default, not an oversight.

- **Anticipation verdict**: ORTHOGONAL.
- **Evidence label**: SOURCED

---

### 6. Miller - Recursive Make Considered Harmful (1998)  ***CLOSEST TO A STATIC BOUND***

- **Citation**: Peter Miller. "Recursive Make Considered Harmful." AUUGN Journal of AUUG
  Inc., Volume 19, Number 1, pages 14-25, 1998. (Originally presented at AUUG'97.)
- **DOI / URL**: No DOI. Author-hosted copy verified live at
  https://aegis.sourceforge.net/auug97.pdf . The 19(1):14-25 citation is corroborated by
  the Crossref reference lists of Mitchell ICFP 2012 (ref e_1_3_2_1_9_1: "Recursive make
  considered harmful, Journal of AUUG Inc, vol 19, first-page 14, 1998"), Licker & Rice
  ICSE 2019 (ref14), and Spall et al. OOPSLA 2020 (ref e_1_2_2_19_1, giving "19, 1
  (1998), 14-25").
- **Access**: Full text.

- **Verbatim quote - S3.3.2 "Repetition", the single most relevant sentence in this
  area for AuxFlow's claim (b)**:
  > "The second traditional solution is to make more than one pass in the top-level
  > Makefile, something like this: [...] This doubles the length of time it takes to
  > perform the build. But that is not all: **there is no guarantee that two passes are
  > enough! The upper bound of the number of passes is not even proportional to the
  > number of modules, it is instead proportional to the number of graph edges which
  > cross module boundaries.**" (emphasis added)

- **Verbatim quote - the cost consequence (S4)**:
  > "The traditional solutions to the problems introduced by recursive make often increase
  > the number of subordinate make invocations beyond the minimum described here; e.g. to
  > perform multiple repetitions (3.3.2), or to overkill cross-module dependencies (3.3.3)."

- **Exact contribution**: Diagnoses recursive Make's incomplete per-directory DAGs as the
  root cause of both unreliability and slowness, and prescribes a single whole-project
  non-recursive Make invocation. In the course of demolishing the "just run it twice"
  workaround, it states a *graph-structural upper bound on the number of build passes*:
  proportional to the number of dependency edges crossing module boundaries.

- **What it does NOT do**: The bound is a qualitative proportionality argument delivered
  in one sentence, not a theorem, not an algorithm, and not a computed quantity. Miller
  offers no method for evaluating it on a given project and no proof. Crucially, the
  bound is about *information propagation delay across artificially partitioned DAGs* -
  each pass pushes information one module boundary further - and NOT about cyclic
  value-carrying facts or convergence of a fixpoint. The whole thrust of the paper is
  that multi-pass builds are the wrong design and should be eliminated, so counting
  passes accurately is presented as a non-goal.

- **Relevance to AuxFlow**: This is the ONLY place in mainstream build-system literature
  that bounds the number of build passes by graph structure. AuxFlow's claim (b) -
  "statically bounding iterations to a fixpoint" - therefore has a genuine, if informal,
  ancestor here. AuxFlow MUST cite Miller and must be careful about the phrasing of any
  novelty claim: "no prior build-system work bounds rebuild rounds by graph structure"
  is FALSE as stated. The accurate claim is narrower: Miller's bound is (i) qualitative,
  (ii) an artefact of partitioning rather than of genuine cyclic data flow, (iii) about
  propagation across an acyclic graph that has been cut up, not about SCCs, and (iv)
  offered as an argument to abandon multi-pass builds rather than to schedule them.
  Note also the structural resemblance worth acknowledging: Miller's "one pass per module
  boundary crossed" is the same shape as AuxFlow's "pass lag" propagation along a longest
  path. AuxFlow should treat this as the informal precursor to its own pass-number
  fixpoint rather than pretend it does not exist.

- **Anticipation verdict**: PARTIAL OVERLAP - the only partial overlap on the
  iteration-bounding claim in this entire area.
- **Evidence label**: SOURCED

---

### 7. GNU Make - "How Makefiles Are Remade" (GNU Make Manual S3.5)

- **Citation**: Richard M. Stallman, Roland McGrath, Paul D. Smith. *GNU Make Manual*,
  Edition 0.77, for GNU Make version 4.4.1. Free Software Foundation, last updated 26
  February 2023. Section 3.5, "How Makefiles Are Remade."
- **DOI / URL**: No DOI (software manual) -
  https://www.gnu.org/software/make/manual/html_node/Remaking-Makefiles.html
- **Access**: Full section text.

- **Verbatim quote (independently re-verified by direct grep)**:
  > "After all makefiles have been checked, if any have actually been changed, `make`
  > starts with a clean slate and reads all the makefiles over again. (It will also
  > attempt to update each of them over again, but normally this will not change them
  > again, since they are already up to date.) Each restart will cause the special
  > variable `MAKE_RESTARTS` to be updated."
  >
  > "This would cause an infinite loop: `make` would constantly remake the makefile and
  > restart, and never do anything else. So, to avoid this, `make` will **not** attempt
  > to remake makefiles which are specified as targets of a double-colon rule with a
  > recipe but no prerequisites."
  >
  > "Phony targets ... have the same effect: they are never considered up-to-date and so
  > an included file marked as phony would cause `make` to restart continuously. To avoid
  > this `make` will not attempt to remake makefiles which are marked phony."

- **Exact contribution**: A genuine, decades-old, mainstream "restart the entire plan and
  redo it" loop in the most widely deployed build tool on earth. Make treats each
  included makefile as a goal, updates it, and if any actually changed, discards
  everything and re-reads from scratch. The restart count is observable at build time via
  `MAKE_RESTARTS`.

- **What it does NOT do**: There is NO numeric bound and NO termination argument in the
  general case. The manual documents exactly two escape hatches against literal infinite
  loops (double-colon rules with a recipe but no prerequisites; phony targets) and is
  otherwise silent. `MAKE_RESTARTS` is a runtime counter, revealed only after the fact -
  Make never predicts it. The restart is triggered by an observed on-disk change, which
  is dynamic checksum-equivalent detection, not analysis.

- **Relevance to AuxFlow**: The closest mainstream *behavioural* analogue to LaTeX's
  rerun-until-stable loop: a real build tool that iterates its own plan to a fixpoint,
  with no bound and no analysis. Strengthens AuxFlow's problem statement (this shape of
  problem is not exotic) while confirming the gap (nobody predicts the count). Also a
  useful precedent for the claim that runtime restart counters are not an oracle.

- **Anticipation verdict**: INFORMS ONLY.
- **Evidence label**: SOURCED

---

### 8. Ninja - manual (v1.13.1), `restat` and `deps`

- **Citation**: Evan Martin et al. *The Ninja build system*, official manual, version
  1.13.1, July 2025.
- **DOI / URL**: No DOI - https://ninja-build.org/manual.html
- **Access**: Full text.

- **Verbatim quote - `restat`**:
  > "`restat` if present, causes Ninja to re-stat the command's outputs after execution of
  > the command. Each output whose modification time the command did not change will be
  > treated as though it had never needed to be built."

- **Verbatim quote - header dependencies must be discovered by the compiler**:
  > "The problem with headers is that the full list of files that a given source file
  > depends on can only be discovered by the compiler ... Some compilers can emit this
  > information while building, and Ninja can use that to get its dependencies perfect."

- **Exact contribution**: `restat` is the early-cutoff mechanism in Ninja: after running a
  command, re-stat the output; if unchanged, suppress downstream propagation.
  `depfile`/`deps=gcc`/`deps=msvc` ingest compiler-emitted dependency edges.

- **What it does NOT do**: The manual documents no loop-until-stable feature, no fixpoint
  concept, and no convergence concept. Ninja requires an acyclic graph; cycles are an
  ordinary validity error with no cycle-breaking strategy. `restat` prunes the *effect*
  of one already-executed edge; it neither counts nor predicts rounds.

- **Relevance to AuxFlow**: Confirms early cutoff is a *dynamic* value-comparison
  mechanism, reinforcing correction 4 (checksum/state comparison is the practical
  baseline). Orthogonal to static prediction.

- **Anticipation verdict**: ORTHOGONAL.
- **Evidence label**: SOURCED

---

### 9. Bazel - static action graph and include scanning

- **Citation**: Bazel official documentation: *Command-Line Reference*
  (https://bazel.build/reference/command-line-reference) and *C++ and Bazel*
  (https://bazel.build/docs/bazel-and-cpp). Accessed 2026-08-27.
- **DOI / URL**: No DOI - as above.
- **Access**: Full pages.

- **Verbatim quote - include scanning, and its disclaimed unsoundness**:
  > "`--[no]cc_include_scanning` ... Whether to narrow inputs to C/C++ compilation by
  > parsing #include lines from input files. This can improve performance and
  > incrementality by decreasing the size of compilation input trees. However, it can
  > also break builds because the include scanner does not fully implement C preprocessor
  > semantics. In particular, it does not understand dynamic #include directives and
  > ignores preprocessor conditional logic. Use at your own risk. Any issues relating to
  > this flag that are filed will be closed."

  The identical text is attached to
  `--[no]experimental_unsupported_and_brittle_include_scanning`. Both default to `false`.

- **Verbatim quote - validation features, not prediction**:
  > "The `layering_check` feature enforces that targets only include headers provided by
  > their direct dependencies."

- **Exact contribution**: Bazel fixes its action graph statically at analysis time. Because
  C/C++ `#include` sets are not statically known, Bazel offers (i) an optional, explicitly
  experimental, explicitly unsupported textual `#include` scanner that *narrows* an
  action's declared inputs, and (ii) `.d`-file ("dotd") pruning, where the compiler is
  actually run and its emitted dependency file is used to validate declarations and prune
  future rebuild triggers. The engine copes with the predefined rules that need dynamic
  dependencies via a *restarting* scheduler.

- **What it does NOT do**: Neither mechanism predicts a count of anything. Include
  scanning predicts an *edge set*, unsoundly, as a performance optimisation, and Google
  ships it off by default with a refuse-to-support notice. Dotd pruning is post-hoc
  discovery from an actual compiler run. Bazel restarts tasks as new dependencies are
  discovered (which is why Mokhov et al. classify it as non-minimal), but that restart
  count is a runtime artefact, never predicted.

- **Relevance to AuxFlow**: This is the closest mainstream analogue to "parse the source
  to predict the build graph", and the industry verdict on it is instructive and
  cautionary: Google implemented exactly that, found it unsound against real preprocessor
  semantics (conditionals, computed includes), and disabled it by default with an
  explicit refusal to support bug reports. The structural parallel to LaTeX is close -
  `\input`, `\include`, conditionals, and macro-computed filenames are the same hazards.
  AuxFlow's declared subset is its defence, and this is strong evidence for why the
  subset must be declared precisely and its escape hatches must map to `UNKNOWN` rather
  than to a confident answer.

- **Anticipation verdict**: INFORMS ONLY (and serves as a cautionary precedent).
- **Evidence label**: SOURCED

---

### 10. Mokhov, Mitchell, Peyton Jones, Marlow - Non-recursive Make Considered Harmful (Haskell 2016)

- **Citation**: Andrey Mokhov, Neil Mitchell, Simon Peyton Jones, Simon Marlow.
  "Non-recursive Make Considered Harmful: Build Systems at Scale." In Proceedings of the
  9th International Symposium on Haskell (Haskell 2016), pages 170-181. ACM, Nara, Japan.
- **DOI / URL**: `10.1145/2976002.2976011` (as printed on the paper's own front matter
  and as cited in Crossref reference lists of Spall et al. 2020, ref e_1_2_2_24_1) -
  https://www.microsoft.com/en-us/research/wp-content/uploads/2016/03/hadrian.pdf
- **Access**: Full text.

- **Verbatim quote - build phases as a hand-derived bound on rounds**:
  > "The GHC build system works around this limitation of Make by dividing the build
  > system into phases, where each phase generates the parts of the build system that are
  > required by subsequent phases. The GHC developers managed to reduce the number of
  > phases to three, by carefully making use of Make's automatic restarting feature where
  > possible. However, explicit phases are a terrible solution for several reasons:
  > • Phases reduce concurrency ... • Knowing what targets to put in each phase requires a
  > deep understanding of generated parts of the build system and their dependencies, and
  > this area of our build system is notoriously difficult to work on."

- **Exact contribution**: Case study demonstrating Make's inadequacy at GHC scale, and the
  redesign onto Shake (Hadrian). Documents build *phases* as the standard workaround for
  the absence of dynamic dependencies.

- **What it does NOT do**: The three-phase count is arrived at by human reasoning about
  the specific build, explicitly described as requiring "a deep understanding" and
  "notoriously difficult". It is not computed by any tool. This is the paper stating the
  cost of the absence of AuxFlow-style analysis, not supplying it.

- **Relevance to AuxFlow**: [INFERENCE] A useful motivating data point: a static
  number-of-rounds figure for a real build was obtained by expert manual analysis at high
  cost, and the authors describe that process as a pathology. It supports the claim that
  deriving round counts automatically has value, while confirming nobody does it.

- **Anticipation verdict**: INFORMS ONLY.
- **Evidence label**: SOURCED

---

### 11. Mitchell - How to write fixed point build rules in Shake (2013)

- **Citation**: Neil Mitchell. "How to write fixed point build rules in Shake, e.g.
  Latex." Stack Overflow question 14622169, asked and self-answered 2013-01-31.
- **DOI / URL**: No DOI -
  https://stackoverflow.com/questions/14622169/how-to-write-fixed-point-build-rules-in-shake-e-g-latex
  Cited as "Mitchell, N. (2013)" in the reference lists of both the ICFP 2018 and JFP 2020
  versions of Build Systems a la Carte, which name it as the recommended encoding for
  LaTeX.
- **Access**: Full question and both answers.

- **Verbatim quote**:
  > "Firstly, note that calling Latex repeatedly does not always produce a fixed point, so
  > make sure you have a bound on the iterations. Also, some distributions (MikTex)
  > provide Latex versions that automatically run as many times as they need to, so if you
  > use those instead the problem goes away."

  The accompanying code implements the bound as a hardcoded constant:
  > `if old == new || i > 100 then copyFile (step i) out else f (i+1)`

- **Exact contribution**: The canonical Shake idiom for LaTeX: unroll the fixpoint into an
  indexed chain of `tempfile.N` targets and stop when consecutive outputs compare equal or
  a hardcoded iteration cap is hit.

- **What it does NOT do**: The "bound" is the literal `100`. There is no derivation, no
  analysis, and no relationship to the document. The convergence test is byte comparison
  of consecutive outputs - i.e. exactly the dynamic checksum baseline.

- **Relevance to AuxFlow**: This is the *state of the practice* that AuxFlow's ICFP-cited
  recommended-encoding predecessor amounts to: a magic constant plus a checksum. It is a
  strong, quotable justification for AuxFlow's problem statement, and it confirms
  correction 4 (checksum/state comparison is the baseline). It also confirms nobody in
  this lineage derives the bound.

- **Anticipation verdict**: INFORMS ONLY.
- **Evidence label**: SOURCED

---

### 12. Spall, Mitchell, Tobin-Hochstadt - Build Scripts with Perfect Dependencies (OOPSLA 2020)

- **Citation**: Sarah Spall, Neil Mitchell, Sam Tobin-Hochstadt. "Build scripts with
  perfect dependencies." Proceedings of the ACM on Programming Languages, Volume 4, Issue
  OOPSLA, pages 1-28. ACM, 13 November 2020.
- **DOI / URL**: `10.1145/3428237` - https://arxiv.org/pdf/2007.12737
- **Access**: Crossref record including full abstract; abstract quoted below.

- **Verbatim quote (abstract, via Crossref)**:
  > "Build scripts for most build systems describe the actions to run, and the
  > dependencies between those actions - but often build scripts get those dependencies
  > wrong. ... We outline a build system where dependencies are not specified, but instead
  > captured by tracing execution. The consequence is that dependencies are always correct
  > by construction and build scripts are easier to write. The simplest implementation of
  > our approach would lose parallelism, but we are able to recover parallelism using
  > speculation."

- **Exact contribution**: Rattle - eliminate dependency declarations entirely; recover
  them by OS-level tracing of actual file accesses; recover lost parallelism by
  speculative execution with hazard detection.

- **What it does NOT do**: Maximally dynamic - it is the *opposite* of static prediction.
  No iteration counting, no fixpoint, no cycle classification.

- **Relevance to AuxFlow**: [INFERENCE] Evidence that the research frontier in build
  systems as of 2020 was moving *away* from static dependency specification and toward
  execution tracing. AuxFlow swims against this current, which is a defensible position
  only if the declared-subset argument is made explicitly.

- **Anticipation verdict**: ORTHOGONAL.
- **Evidence label**: SOURCED (abstract and metadata; full PDF not opened)

---

### 13. The Makefile / build-script static-analysis literature (collectively)

Verified as a group because the finding is uniform. All DOIs Crossref-verified.

- **SYMake (full paper)**: Ahmed Tamrawi, Hoan Anh Nguyen, Hung Viet Nguyen, Tien N.
  Nguyen. "Build code analysis with symbolic evaluation." ICSE 2012, Zurich, pages
  650-660. IEEE. DOI `10.1109/ICSE.2012.6227152`.
  > "SYMake provides a symbolic evaluation algorithm that processes Makefiles and produces
  > a symbolic dependency graph (SDG), which represents the build dependencies (i.e.
  > rules) among files via commands. ... We have used SYMake to develop algorithms and a
  > tool 1) to detect several types of code smells and errors in Makefiles, and 2) to
  > support build code refactoring, e.g. renaming a variable/target even if its name is
  > fragmented and built from multiple substrings."
- **SYMake (tool demo)**: same authors. "SYMake: a build code analysis and refactoring
  tool for makefiles." ASE 2012, pages 366-369. ACM. DOI `10.1145/2351676.2351749`.
- **MAKAO (tool demo)**: Bram Adams, Herman Tromp, Kris de Schutter, Wolfgang de Meuter.
  "MAKAO." ICSM 2007, Paris, pages 517-518. IEEE. DOI `10.1109/ICSM.2007.4362678`.
  **CORRECTION**: the DOI in the task brief, `10.1109/ICSM.2007.4362624`, is a different
  (also real) paper by the same group: "Design recovery and maintenance of build systems",
  ICSM 2007, pages 114-123. Both DOIs independently re-verified by me via Crossref.
- **Bezemer et al.**: Cor-Paul Bezemer, Shane McIntosh, Bram Adams, Daniel M. German,
  Ahmed E. Hassan. "An empirical study of unspecified dependencies in make-based build
  systems." Empirical Software Engineering 22(6):3117-3148, 2017. Springer.
  DOI `10.1007/s10664-017-9510-8`.
  > "To uncover unspecified dependencies in make-based build systems, we use an approach
  > that combines a conceptual model of the dependencies specified in the build system
  > with a concrete model of the files and processes that are actually exercised during
  > the build ... we find that unspecified dependencies are common."
- **Licker & Rice**: Nandor Licker, Andrew Rice. "Detecting Incorrect Build Rules." ICSE
  2019, Montreal, pages 1234-1244. IEEE. DOI `10.1109/ICSE.2019.00125`.
  **CORRECTION**: the DOI in the task brief, `10.1109/ICSE.2019.00109`, resolves to an
  unrelated paper (FOCUS, an API recommender system). Corrected DOI independently
  re-verified by me via Crossref.
  > "We automatically uncover such missing dependencies through a novel method that we
  > call build fuzzing. The correctness of build definitions is verified by modifying
  > files in a project, triggering incremental builds and comparing the set of changed
  > files to the set of expected changes."
- **VeriBuild**: Gang Fan, Chengpeng Wang, Rongxin Wu, Xiao Xiao, Qingkai Shi, Charles
  Zhang. "Escaping Dependency Hell: Finding Build Dependency Errors with the Unified
  Dependency Graph." ISSTA 2020, pages 463-474. ACM. DOI `10.1145/3395363.3397388`.
  Its related-work section is the most useful single admission in this group, because it
  taxonomises the whole sub-field:
  > "We classify these techniques into three categories based on how ... dependency graphs
  > represent the build targets and their dependencies. The first category constructs the
  > static dependency graph via statically analyzing the build scripts and the executed
  > shell commands ... this category of techniques can only detect bad smells in build
  > definitions (e.g., the cyclic dependency issue). The second category constructs the
  > dynamic dependence graph via monitoring and capturing the actual dependency in build
  > processes ... The third category leverages both the static and dynamic dependency
  > graphs and cross-references them to discover the inconsistencies."

- **Exact contribution (collective)**: Static, dynamic, and hybrid techniques for
  detecting *dependency-graph correctness* defects - missing edges, redundant edges,
  spurious edges, file-target inconsistency, race conditions - plus visualisation,
  reverse-engineering, and refactoring support.

- **What it does NOT do**: Not one of these derives, predicts, or bounds how many times a
  build rule executes, how many rebuild rounds a build requires, or whether a build
  reaches a fixpoint. Every formalism used across the group (SYMake's symbolic dependency
  graph and T-model, MAKAO's dependency graph, VeriBuild's unified dependency graph) is a
  reachability or set-membership structure with no notion of multiplicity, round count, or
  converging state sequence. Where cycles appear at all they are treated as a *bad smell*
  to be reported and eliminated - never as a structure to be classified as convergent or
  divergent. VeriBuild's own taxonomy above confirms this framing for the whole sub-field.

- **Relevance to AuxFlow**: Establishes that "static analysis of build scripts" is a real
  and active research area whose entire output is orthogonal to AuxFlow's question. This
  is the strongest available evidence for the gap AuxFlow claims on (b) and (c).
  Simultaneously it is a warning about positioning: AuxFlow's *diagnosis* output (naming
  offending facts at source level) closely resembles what these tools do for dependency
  defects, so the diagnosis component should be presented as an application of the
  classification, not as an independent contribution.

- **Anticipation verdict**: ORTHOGONAL (all six).
- **Evidence label**: SOURCED

---

### 14. Build-outcome prediction (BuildFast)

- **Citation**: Bihuan Chen, Linlin Chen, Chen Zhang, Xin Peng. "BuildFast: History-Aware
  Build Outcome Prediction for Fast Feedback and Reduced Cost in Continuous Integration."
  ASE 2020, pages 42-53. ACM. DOI `10.1145/3324884.3416616`.
- **DOI / URL**: https://chenbihuan.github.io/paper/ase20-chen-buildfast.pdf
- **Access**: Full text (author copy).

- **Verbatim quote**:
  > "Build outcome prediction ... leverages machine learning techniques to predict build
  > outcomes such that the cost of the builds that are predicted to pass can be reduced."

- **Exact contribution**: An ML classifier over historical git and CI metadata (code
  churn, AST-level diffs, commit counts, prior build outcome, failure ratios) predicting a
  categorical build outcome: passed / errored / failed.

- **What it does NOT do**: It is not a static source analysis - its features are
  repository-history statistics. It has no iteration-count, rebuild-count, or
  pass-count target variable anywhere in its feature or label tables.

- **Relevance to AuxFlow**: Confirms that "predicting build behaviour" in the literature
  means predicting duration or pass/fail from history, never predicting a number of
  rounds from source structure.

- **Anticipation verdict**: ORTHOGONAL.
- **Evidence label**: SOURCED

---

## Negative results

Exact queries that found nothing relevant. All are re-runnable.

1. `build system research "idempotent build" OR "build convergence" OR "repeated builds until fixpoint" bounding number of build rounds graph diameter`
   - ~99 results examined. Zero build-system papers. All substantive hits were generic
     lattice/dataflow fixpoint theory (Kleene fixpoint theorem, Knaster-Tarski, monotone
     frameworks, lattice-height bound O(N*h), acyclic-graph stabilisation in |V|-2
     iterations). That material belongs to the attribute-grammar / abstract-interpretation
     areas, not to build systems.

2. `"build system" research statically bound "number of iterations" OR "number of rounds" rebuild fixpoint SCC longest path prediction`
   - ~60 results examined. Zero relevant. Hits were topological-sort tutorials,
     critical-path project-management pages, patents on build-graph caching, and one
     unrelated Python type-inference tool.

3. `build system OR incremental computation classify cyclic dependencies "benign" versus divergent terminating cycle static analysis guarantee fixpoint reached`
   - ~40 results examined. No benign-versus-divergent cycle taxonomy exists in build-system
     research. The only "classification" available anywhere is the generic
     monotone-plus-finite-lattice sufficient condition, which is assumed rather than
     checked, and is not a build-systems result.

4. `"build system" termination analysis prove build terminates static guarantee number of passes document compilation predict`
   - ~27 results examined. Zero relevant. Confirms build-system termination is universally
     obtained by *assuming* acyclicity, never by analysis.

5. `Erdweg Lichter cyclic build dependencies build system "cycle" sound incremental follow-up paper`
   and `"cyclic build dependencies" "fixpoint" build system paper`
   - ~18 results examined. NO follow-up paper on cyclic builds by the Pluto group was
     found. Cycle support is contained entirely within the OOPSLA 2015 paper (S3.4, S4.6,
     S5.2). Searches returned only the 2015 paper plus secondary commentary. I therefore
     record: **no cyclic-builds follow-up paper located** (marked UNVERIFIED as to
     non-existence - absence of evidence from these queries only).

6. `predicting CI build failures machine learning "iteration count" OR "number of rebuilds"`
   - No paper found predicting an iteration or rebuild count. All predict pass/fail or
     wall-clock duration.

7. Grep of the Tup technical report full text for
   `(?i)cycle|cyclic|acyclic|iterat|converge|fixpoint|repeat|circular|latex`
   - Only hits were "Edit-Compile-Test cycle" and "directed acyclic graph". No iteration,
     fixpoint, or cycle-handling concept exists in the document.

8. Grep of the Shake ICFP 2012 paper full text for
   `(?i)latex|fixed point|fixpoint|converge|iterat|cycle|cyclic|terminat|well-defined|undecid`
   - Only hits were the two S2.2 well-definedness passages. Shake's paper contains no
     LaTeX example, no fixpoint machinery, and no cycle handling.

9. Grep of Bazel's command-line reference for `hdrs_check|strict_include|layering_check`
   - No matches. These are BUILD-file/toolchain-feature constructs, not command-line
     flags; located instead on the separate "C++ and Bazel" documentation page.

10. Attempted primary-source routes that FAILED (recorded so they are not retried blindly):
    `http://erdweg.org/publications/pluto-incremental-build.pdf` (301 to a dead
    uni-mainz path); `https://erdweg.org/publications.html` (TLS certificate error);
    `https://www.researchgate.net/publication/301447217` (HTTP 403);
    `https://api.semanticscholar.org/graph/v1/paper/6729944...` (API failure);
    `https://dblp.org/rec/conf/oopsla/ErdwegLW15.html` and `.bib`, `https://dblp.org/pid/07/9407.html`,
    `https://dblp.org/search/publ/api?...` (all socket resets - DBLP unreachable from this
    environment throughout the audit).

---

## Summary for the audit

- **(a) Is the static-versus-dynamic dependency gap well studied in build systems? YES,
  emphatically, and it is a solved-and-formalised question.** Mokhov, Mitchell & Peyton
  Jones (ICFP 2018, DOI 10.1145/3236774; JFP 2020, DOI 10.1017/S0956796820000088) make it
  a *type-level* distinction: `Task Applicative` = dependencies determinable statically
  "by looking at the formulae, without 'computing' them"; `Task Monad` = dependencies
  "determined by values of intermediate computations". Erdweg, Lichter & Weiel (OOPSLA
  2015, DOI 10.1145/2814270.2814316) and Mitchell (ICFP 2012, DOI 10.1145/2364527.2364538)
  supply the systems side. AuxFlow MUST NOT frame the static/dynamic dependency gap as an
  unstudied observation. It is the organising axis of the field's canonical paper.

- **(b) Does any build-system work statically bound the number of iterations to a
  fixpoint? Essentially NO - but the honest answer is "one informal precursor exists".**
  Miller 1998 states that for multi-pass recursive Make "there is no guarantee that two
  passes are enough! The upper bound of the number of passes ... is proportional to the
  number of graph edges which cross module boundaries." That is a graph-structural bound
  on build passes and AuxFlow cannot claim the idea is unprecedented. But it is one
  qualitative sentence, with no algorithm, no proof, about propagation delay across an
  artificially partitioned *acyclic* graph rather than about cyclic data flow, and offered
  as an argument to abandon multi-pass builds. Everything else in the field either
  hardcodes a constant (Excel's iterative-calculation cap N=100; Mitchell 2013's `i > 100`)
  or derives the bound by expensive human reasoning (GHC's three phases). No tool computes
  it.

- **(c) Does any build-system work classify cyclic build dependencies as benign versus
  divergent? NO.** Pluto is the only build system with first-class cycle support, and it
  explicitly refuses to classify: the developer attaches a handler, and the fixpoint
  handler ships with the printed disclaimer that it "does not guarantee a fixpoint will be
  reached. The builders in the cycle need to be designed to take part in a fixpoint
  compilation." Mokhov et al. *name* the divergent category for LaTeX ("bistable or
  diverging") without offering any means to detect it, and note only that some frameworks
  support cycles "under the assumption that tasks are monotonic in a certain sense" -
  monotonicity assumed, never verified. VeriBuild's survey confirms that where the
  static-analysis literature touches cycles at all, it treats them as a bad smell to
  eliminate, not a structure to classify.

- **(d) MOST DANGEROUS PRIOR ART: Pluto - Erdweg, Lichter & Weiel, OOPSLA 2015, DOI
  10.1145/2814270.2814316.** It is dangerous on four axes at once, and it is dangerous in
  a way that is easy to underestimate from the title alone. Its running example is a LaTeX
  + BibTeX builder. It identifies the `.aux` self-cycle explicitly ("the Latex builder is
  in a cycle by itself because it reads from and writes to the same aux file") and the
  LaTeX/BibTeX cycle. It ships a `FixpointCycleHandler` that iterates the cycle to
  stability. And its BibTeX builder uses "a custom stamper that parses the aux file,
  extracts the bibliography name and the set of referenced citation keys, and uses them as
  a stamp" - which is sub-file, semantic, *fact-level* dependency granularity on aux
  content, arrived at dynamically. AuxFlow's instance-level-fact granularity is therefore
  not novel as an idea; only its static derivation is.

- **The single sharpest threat is one sentence in Pluto S3.3**: "In the case of Latex
  where even parsing is undecidable [4], soundly detecting dependencies is a lost cause."
  Reference [4] is Erdweg & Ostermann, "Featherweight TeX and Parser Correctness", SLE
  2010, DOI 10.1007/978-3-642-19440-5_26. This is not an oversight AuxFlow can exploit; it
  is a considered rejection, published at OOPSLA, by an author who had already written the
  formal paper on TeX parsing. AuxFlow must confront it in the first two pages. Its only
  available answer is the declared subset, and that answer is only credible if the subset
  is specified precisely and every escape from it maps to `UNKNOWN`.

- **Bazel is the industry-scale cautionary tale for AuxFlow's method.** Google built
  exactly "parse the source to predict the build graph" for C/C++, and ships it as
  `--experimental_unsupported_and_brittle_include_scanning`, default off, documented as
  breaking builds because "the include scanner does not fully implement C preprocessor
  semantics. In particular, it does not understand dynamic #include directives and ignores
  preprocessor conditional logic. Use at your own risk. Any issues relating to this flag
  that are filed will be closed." The failure modes named - conditionals and computed
  filenames - map one-to-one onto LaTeX conditionals and macro-computed `\input` arguments.

- **GNU Make's makefile-remaking restart is the closest mainstream behavioural analogue**
  to LaTeX's rerun-until-stable loop: Make "starts with a clean slate and reads all the
  makefiles over again", counts restarts in `MAKE_RESTARTS`, and documents no bound at all
  - only two ad-hoc escape hatches against literal infinite loops. A real, ubiquitous
  build tool iterates its own plan to a fixpoint with no analysis whatsoever. This
  supports AuxFlow's problem statement and confirms the gap simultaneously.

- **Corrections 3 and 4 are reinforced by this area.** Pluto states that "even
  Latex-specific build systems like latexmk use unsound heuristics to detect dependencies";
  Mitchell's ICFP-cited 2013 LaTeX recipe converges by byte-comparing consecutive outputs
  with a hardcoded cap; Ninja's `restat` and Shake's unchanging-results optimisation are
  both output-value comparison. Checksum/state comparison is unambiguously the practical
  baseline across the whole field.

- **What AuxFlow can still legitimately claim from this area** (i.e. what is genuinely
  absent from every source above): instance-level fact nodes derived *statically from
  source* rather than discovered at runtime; pass-lag edges and a statically propagated
  per-fact stable pass number; a taint analysis distinguishing facts that influence *how
  much content is generated* from facts that do not; and a resulting
  BENIGN_CYCLIC-versus-AMPLIFYING classification with source-level attribution. No
  build-system work does any of these. Note the caveat that the pass-number fixpoint
  machinery itself is attribute-grammar prior art (area A), not new here - the
  build-systems contribution is only the application to a build convergence question.

- **Two DOI errors in the audit brief are corrected here and were each verified twice
  against Crossref**: Licker & Rice ICSE 2019 is `10.1109/ICSE.2019.00125` (not `.00109`,
  which is the unrelated FOCUS paper); the MAKAO tool demo is `10.1109/ICSM.2007.4362678`
  (`10.1109/ICSM.2007.4362624` is a separate, also real, ICSM 2007 paper by the same group,
  "Design recovery and maintenance of build systems", pages 114-123).

- **Net verdict for area E**: The static/dynamic framing is fully anticipated and AuxFlow
  must concede it. The iteration-bounding claim has one informal precursor (Miller 1998)
  that must be cited and distinguished. The cycle-classification claim is genuinely
  unanticipated in build systems. The domain-specific claim to have found the LaTeX aux
  cycle is fully anticipated by Pluto and must be dropped.
