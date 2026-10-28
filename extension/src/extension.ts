import * as path from 'node:path';
import { spawn, ChildProcessWithoutNullStreams } from 'node:child_process';
import * as vscode from 'vscode';

type State = 'CERTIFIED' | 'BENIGN_CYCLIC' | 'AMPLIFYING' | 'UNKNOWN';
interface CheckDiagnostic {
    file: string;
    line: number;
    column: number;
    end_line: number;
    end_column: number;
    severity: 'error' | 'warning';
    message: string;
}
interface CheckReport {
    file: string;
    ok: boolean;
    errors: number;
    warnings: number;
    convergence: State;
    diagnostics: CheckDiagnostic[];
}
interface ProcessResult {
    code: number | null;
    stdout: string;
    stderr: string;
}

let collection: vscode.DiagnosticCollection;
let status: vscode.StatusBarItem;
let output: vscode.OutputChannel;
let timer: NodeJS.Timeout | undefined;
let child: ChildProcessWithoutNullStreams | undefined;
let generation = 0;
let lastFailure = '';
let extensionRoot: string;
let disposed = false;

function setStatus(text: string, tooltip: string): void {
    status.text = `$(pulse) AuxFlow: ${text}`;
    status.tooltip = tooltip;
    status.show();
}

function fail(message: string): void {
    collection.clear();
    setStatus('Unavailable', message);
    output.appendLine(message);
    if (message !== lastFailure) {
        lastFailure = message;
        void vscode.window.showErrorMessage(message, 'Show AuxFlow Output').then((action) => {
            if (action) {
                output.show(true);
            }
        });
    }
}

function cancel(): number {
    generation++;
    if (timer) {
        clearTimeout(timer);
        timer = undefined;
    }
    if (child) {
        child.kill();
        child = undefined;
    }
    return generation;
}

function tex(document: vscode.TextDocument): boolean {
    return document.uri.scheme === 'file' && document.uri.fsPath.toLowerCase().endsWith('.tex');
}

function mainFile(document: vscode.TextDocument): string {
    const folder = vscode.workspace.getWorkspaceFolder(document.uri);
    const setting = vscode.workspace
        .getConfiguration('auxflow', document.uri)
        .get<string>('mainFile', '')
        .trim();
    if (!setting) {
        return document.uri.fsPath;
    }
    if (!folder) {
        throw new Error('auxflow.mainFile requires a workspace folder.');
    }
    if (path.isAbsolute(setting)) {
        throw new Error('auxflow.mainFile must be relative to its workspace folder.');
    }
    const target = path.resolve(folder.uri.fsPath, setting);
    const relative = path.relative(folder.uri.fsPath, target);
    if (relative === '..' || relative.startsWith(`..${path.sep}`)) {
        throw new Error('auxflow.mainFile must remain inside its workspace folder.');
    }
    if (!target.toLowerCase().endsWith('.tex')) {
        throw new Error('auxflow.mainFile must name a .tex file.');
    }
    return target;
}

function currentDocument(fallback?: vscode.TextDocument): vscode.TextDocument | undefined {
    const active = vscode.window.activeTextEditor?.document;
    return active && tex(active) ? active : fallback && tex(fallback) ? fallback : undefined;
}

function sourcesFor(): Record<string, string> {
    const sources: Record<string, string> = {};
    for (const open of vscode.workspace.textDocuments) {
        if (tex(open)) {
            sources[open.uri.fsPath] = open.getText();
        }
    }
    return sources;
}

function runPython(
    executable: string,
    args: string[],
    stdin: string,
    env: NodeJS.ProcessEnv,
): Promise<ProcessResult> {
    return new Promise((resolve, reject) => {
        const process = spawn(executable, args, {
            cwd: extensionRoot,
            env,
            stdio: ['pipe', 'pipe', 'pipe'],
            shell: false,
        });
        child = process;
        let stdout = '';
        let stderr = '';
        process.stdout.setEncoding('utf8');
        process.stderr.setEncoding('utf8');
        process.stdout.on('data', (chunk: string) => {
            stdout += chunk;
        });
        process.stderr.on('data', (chunk: string) => {
            stderr += chunk;
        });
        process.on('error', reject);
        process.on('close', (code) => {
            if (child === process) {
                child = undefined;
            }
            resolve({ code, stdout, stderr });
        });
        process.stdin.on('error', () => {
            /* A failed process reports its exit status and stderr. */
        });
        process.stdin.end(stdin);
    });
}

function validReport(value: unknown): value is CheckReport {
    if (!value || typeof value !== 'object') {
        return false;
    }
    const report = value as Partial<CheckReport>;
    return (
        typeof report.file === 'string' &&
        typeof report.ok === 'boolean' &&
        Number.isInteger(report.errors) &&
        Number.isInteger(report.warnings) &&
        ['CERTIFIED', 'BENIGN_CYCLIC', 'AMPLIFYING', 'UNKNOWN'].includes(report.convergence ?? '') &&
        Array.isArray(report.diagnostics) &&
        report.diagnostics.every(
            (entry) =>
                entry &&
                typeof entry.file === 'string' &&
                [entry.line, entry.column, entry.end_line, entry.end_column].every(
                    (n) => Number.isInteger(n) && n >= 1,
                ) &&
                ['error', 'warning'].includes(entry.severity) &&
                typeof entry.message === 'string',
        )
    );
}

function position(file: string, line: number, column: number): vscode.Position {
    const document = vscode.workspace.textDocuments.find(
        (open) => open.uri.scheme === 'file' && open.uri.fsPath === file,
    );
    const lineIndex = line - 1;
    if (!document || lineIndex < 0 || lineIndex >= document.lineCount) {
        return new vscode.Position(Math.max(0, lineIndex), Math.max(0, column - 1));
    }
    const text = document.lineAt(lineIndex).text;
    const utf16Column = Array.from(text)
        .slice(0, column - 1)
        .join('').length;
    return new vscode.Position(lineIndex, utf16Column);
}

function publish(report: CheckReport): void {
    const byFile = new Map<string, vscode.Diagnostic[]>();
    for (const entry of report.diagnostics) {
        const start = position(entry.file, entry.line, entry.column);
        const end = position(entry.file, entry.end_line, entry.end_column);
        const diagnostic = new vscode.Diagnostic(
            new vscode.Range(start, end.isBefore(start) ? start : end),
            entry.message,
            entry.severity === 'error' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning,
        );
        diagnostic.source = 'AuxFlow';
        const list = byFile.get(entry.file) ?? [];
        list.push(diagnostic);
        byFile.set(entry.file, list);
    }
    collection.clear();
    for (const [file, entries] of byFile) {
        collection.set(vscode.Uri.file(file), entries);
    }
    lastFailure = '';
    const label: Record<State, string> = {
        CERTIFIED: 'Certified',
        BENIGN_CYCLIC: 'Benign cyclic',
        AMPLIFYING: 'Amplifying risk',
        UNKNOWN: 'Unknown certainty',
    };
    setStatus(
        label[report.convergence],
        `AuxFlow convergence: ${report.convergence}. ${report.diagnostics.length} diagnostic(s). UNKNOWN means the analysis cannot establish convergence; AMPLIFYING indicates a convergence risk.`,
    );
    status.backgroundColor =
        report.convergence === 'AMPLIFYING' || report.convergence === 'UNKNOWN'
            ? new vscode.ThemeColor('statusBarItem.warningBackground')
            : undefined;
}

async function check(document: vscode.TextDocument, id: number): Promise<void> {
    try {
        const root = mainFile(document);
        const config = vscode.workspace.getConfiguration('auxflow', document.uri);
        const executable = config.get<string>('pythonPath', 'python3');
        if (!executable.trim()) {
            throw new Error('auxflow.pythonPath must name a Python 3.12+ executable.');
        }
        const env = {
            ...process.env,
            PYTHONPATH: path.join(extensionRoot, 'python'),
            PYTHONNOUSERSITE: '1',
            PYTHONSAFEPATH: '1',
            AUXFLOW_NO_UPDATE_CHECK: '1',
        };
        setStatus('Checking', `Analyzing ${root}`);
        const version = await runPython(
            executable,
            ['-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 2)'],
            '',
            env,
        );
        if (id !== generation || disposed) {
            return;
        }
        if (version.code !== 0) {
            throw new Error(
                version.code === 2
                    ? 'AuxFlow requires Python 3.12 or newer.'
                    : `Cannot start Python: ${version.stderr.trim() || `exit ${version.code}`}`,
            );
        }
        const result = await runPython(
            executable,
            ['-m', 'auxflow.cli', 'check', '--json', '--sources-stdin', root],
            JSON.stringify({ sources: sourcesFor() }),
            env,
        );
        if (id !== generation || disposed) {
            return;
        }
        if (result.code !== 0 && result.code !== 1) {
            throw new Error(
                `AuxFlow check failed (exit ${result.code}): ${result.stderr.trim() || result.stdout.trim() || 'no details'}`,
            );
        }
        let report: unknown;
        try {
            report = JSON.parse(result.stdout);
        } catch {
            throw new Error(
                `AuxFlow returned invalid JSON: ${result.stderr.trim() || result.stdout.slice(0, 200)}`,
            );
        }
        if (!validReport(report)) {
            throw new Error('AuxFlow returned an invalid diagnostic report.');
        }
        const errors = report.diagnostics.filter((entry) => entry.severity === 'error').length;
        if (
            report.errors !== errors ||
            report.warnings !== report.diagnostics.length - errors ||
            report.ok !== (errors === 0) ||
            result.code !== Number(errors > 0)
        ) {
            throw new Error('AuxFlow returned inconsistent diagnostic counts or exit status.');
        }
        publish(report);
    } catch (error) {
        if (id !== generation || disposed) {
            return;
        }
        status.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
        fail(`AuxFlow: ${error instanceof Error ? error.message : String(error)}`);
    }
}

function schedule(document?: vscode.TextDocument, delay = 0): void {
    const id = cancel();
    if (!document || !tex(document)) {
        collection.clear();
        status.backgroundColor = undefined;
        setStatus('Idle', 'Open a .tex file to analyze it.');
        return;
    }
    timer = setTimeout(() => {
        timer = undefined;
        void check(document, id);
    }, delay);
}

export function activate(context: vscode.ExtensionContext): void {
    disposed = false;
    extensionRoot = context.extensionPath;
    collection = vscode.languages.createDiagnosticCollection('auxflow');
    status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
    output = vscode.window.createOutputChannel('AuxFlow');
    context.subscriptions.push(
        collection,
        status,
        output,
        vscode.workspace.onDidOpenTextDocument((document) => {
            if (tex(document)) {
                schedule(currentDocument(document));
            }
        }),
        vscode.workspace.onDidChangeTextDocument((event) => {
            if (tex(event.document)) {
                const delay = vscode.workspace
                    .getConfiguration('auxflow', event.document)
                    .get<number>('debounceMilliseconds', 350);
                schedule(currentDocument(event.document), delay);
            }
        }),
        vscode.workspace.onDidSaveTextDocument((document) => {
            if (tex(document)) {
                schedule(currentDocument(document));
            }
        }),
        vscode.workspace.onDidCloseTextDocument((document) => {
            if (tex(document)) {
                collection.delete(document.uri);
                schedule(currentDocument());
            }
        }),
        vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('auxflow')) {
                cancel();
                collection.clear();
                status.backgroundColor = undefined;
                schedule(currentDocument());
            }
        }),
        vscode.window.onDidChangeActiveTextEditor((editor) => {
            if (editor?.document && tex(editor.document)) {
                schedule(editor.document);
            }
        }),
        vscode.commands.registerCommand('auxflow.checkNow', () => schedule(currentDocument())),
    );
    setStatus('Idle', 'Open a .tex file to analyze it.');
    schedule(currentDocument());
}

export function deactivate(): void {
    disposed = true;
    cancel();
}
