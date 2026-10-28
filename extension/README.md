# AuxFlow for VS Code

AuxFlow checks LaTeX `.tex` sources while you edit. It reports parser and semantic diagnostics in Problems and displays the static convergence classification in the status bar. It **does not run TeX**, build a PDF, or invoke `auxflow run`.

## Install and update from GitHub

Download `auxflow-<version>.vsix` from the [GitHub Releases page](https://github.com/upayanmazumder/auxflow/releases). In VS Code, open the Extensions view, select **Install from VSIX...**, and choose the downloaded file. Alternatively, run `code --install-extension auxflow-<version>.vsix` from a terminal.

To update, download a newer VSIX from GitHub Releases and install it the same way. VS Code does not automatically update extensions installed from a VSIX. This extension is not published to the Visual Studio Marketplace.

## Requirements

- VS Code 1.85 or newer in a trusted workspace.
- Python 3.12 or newer available on the extension host (the machine where workspace extensions run). The default executable is `python3`; set `auxflow.pythonPath` if needed. The analyzer's dependency-free Python source is bundled in the extension; a separate AuxFlow installation is not required.

AuxFlow is a static analysis tool, not a replacement for a TeX compiler. Unsupported constructs can make its convergence classification uncertain. **UNKNOWN** does not mean the document is safe or convergent; **AMPLIFYING** signals a possible convergence risk. CERTIFIED and BENIGN_CYCLIC describe AuxFlow's model, not a guarantee about external tools or arbitrary TeX macros.

## Using the extension

Open a `.tex` file to check it. Editing triggers a debounced check; opening and saving also trigger checks. The extension sends the current contents of all open `.tex` buffers to the bundled analyzer, including unsaved edits and unsaved new files. Diagnostics may appear in included files as well as the main file. Close a file to remove its diagnostics; the current document is checked again. Run **AuxFlow: Check TeX Sources** from the Command Palette for an immediate check.

Set `auxflow.mainFile` to the main `.tex` file **relative to its workspace folder** when editing included files. Leave it empty (the default) to use the active `.tex` file as the main file. In multi-root workspaces, set the option separately per folder. `auxflow.debounceMilliseconds` defaults to 350 ms. `auxflow.pythonPath` defaults to `python3`.

If Python is unavailable, too old, or analysis fails, AuxFlow clears stale diagnostics, displays **Unavailable** instead of a success classification, and reports the error in the AuxFlow output channel. Automatic update notices are disabled. The extension launches only the Python analyzer's `check` command, never a TeX engine.

Source and issues: https://github.com/upayanmazumder/auxflow. Licensed under MIT.
