# AuxFlow demonstration documents

These small documents show CERTIFIED, AMPLIFYING, and UNKNOWN results without
changing your project files. Run these commands from the repository root:

```sh
auxflow check examples/quickstart/simple.tex
auxflow classify examples/quickstart/simple.tex
auxflow graph examples/quickstart/simple.tex -o /tmp/auxflow-simple.dot

auxflow check examples/quickstart/multifile/main.tex
auxflow classify examples/quickstart/multifile/main.tex
auxflow plan --explain examples/quickstart/multifile/main.tex

auxflow check examples/quickstart/custom-class/main.tex
auxflow classify examples/quickstart/custom-class/main.tex

auxflow classify examples/quickstart/feedback.tex
auxflow plan --explain examples/quickstart/feedback.tex
```

`simple.tex` has a label and a reference. Its predicted schedule is two runs.
`multifile/main.tex` includes a section file and a table of contents. Its predicted schedule is three runs.
`feedback.tex` uses a page reference to control a loop that adds pages. AuxFlow reports AMPLIFYING and refuses a build plan. The last command exits with status 1 on purpose.
`custom-class/main.tex` uses a local class that loads `geometry`.
The check names the package and its class file. Classification stays UNKNOWN because
AuxFlow does not model the class's effects.

Use `auxflow classify -v FILE` for detailed locations of unsupported constructs in an UNKNOWN document.
Do not use `--force` on the feedback example during a live demo. It runs a potentially divergent TeX document under a cap.

## Thesis demonstration

If your VIT thesis files remain at the path below, run:

```sh
auxflow check /home/upayan/Downloads/Thesis_content/Thesis_content_v1.0/thesis.tex
auxflow classify /home/upayan/Downloads/Thesis_content/Thesis_content_v1.0/thesis.tex
```

The check lists packages loaded by the local `VITSCOPEThesis.cls` file.
The classifier reports UNKNOWN and names the local class and unsupported commands.
It does not claim a run-count bound for this thesis. No TeX engine runs during these checks.
Copy the thesis elsewhere only if you want to share it. Point the commands at its new path.
